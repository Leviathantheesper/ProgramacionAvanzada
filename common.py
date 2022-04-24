#! ../venv/bin/python3.8
"""
January the 21er, 2022
CDMX
F. Sagols.

Trading in Interactive Brokers Project

Common tools for any algorithmic trading project.
"""

import sys
import re
import math
import logging
import select
from logging.handlers import TimedRotatingFileHandler
from os import path
import os
import datetime
from datetime import timedelta
from itertools import chain, combinations


def powerset(iterable):
    """
    Computes the power set of one iterable.

    Parameters
    ----------
    iterable : iterable
        Representation of some set.

    Returns
    -------
        Iterable power set
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def assign_tasks(tasks, processor, processors):
    """
    Given a list of tasks this method returns the sub-list of tasks that should
    be performed by processor number 'processor'. The total number of
    processors is 'processors'. The assignation is fair.

    Parameters
    ----------
    tasks : list
        Tasks to be performed
    processor : int
        Number of processor.
    processors : int
        Total number of processors

    Returns
    -------
        The sub-lists of tasks for 'processor''.
    """
    tasks_for_processor = math.ceil(len(tasks) / processors)
    start = tasks_for_processor * processor
    end = start + tasks_for_processor
    return tasks[start:end]


class Dates:
    """
    Dates iterator. You define an initial and final base_date, and it iterates
    the time period in one day steps.
    """
    def __init__(self, initial_date=None, end_date=None, step=1):
        """
        Creates a dates iterator.

        PARAMETERS
        -----------
        initial_date : datetime.pyi
            Initial
        end_date : datetime.pyi
            End base_date.
        """
        self.step = step
        if initial_date and end_date:
            assert initial_date <= end_date, \
                'The starting base_date must be lower or equal than the '
            'ending one'
        self.initial_date = initial_date
        self.end_date = end_date
        if not end_date or (initial_date and end_date):
            self.date = self.initial_date
        else:
            self.date = self.end_date

    def __iter__(self):
        """
        Returns the initial base_date
        """
        return self

    def __next__(self):
        """
        Returns the next base_date
        """
        aux = self.date
        if self.initial_date and self.end_date:
            if self.date > self.end_date:
                raise StopIteration
            self.date += timedelta(days=self.step)
            return aux.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.initial_date is None:
            # TODO: I don't understand why constants like -180, -7 or 4
            # are used.
            if self.date <= self.end_date + timedelta(days=-180):
                raise StopIteration
            self.date += timedelta(days=-7)
            return [
                aux.replace(hour=0, minute=0, second=0, microsecond=0) +
                timedelta(days=-4),
                aux.replace(hour=0, minute=0, second=0, microsecond=0)
            ]
        if self.end_date is None:
            if self.date >= self.initial_date + timedelta(days=180):
                raise StopIteration
            self.date += timedelta(days=7)
            return [
                aux.replace(hour=0, minute=0, second=0, microsecond=0),
                aux.replace(hour=0, minute=0, second=0, microsecond=0) +
                timedelta(days=4)
            ]


def date_in_spanish(date):
    """
    Translates a string base_date to spanish. That is, all references to months
    abbreviations like 'Jan', 'Feb', 'Mar' and so on are changed to 'Ene',
    'Feb', 'Mar', respectively.

    Parameters
    ----------
    date : str
        Date to be translated.

    Returns
    ------
        str
        The translated base_date.

    Examples
    --------
    >>> date_in_spanish("23-Apr-2021")
    23-Abr-2021 
    >>> date_in_spanish("Dec-24-2020")
    Dic-24-2020
    """
    month_trans = {
        'Jan': 'Ene',
        'Feb': 'Feb',
        'Mar': 'Mar',
        'Apr': 'Abr',
        'May': 'May',
        'Jun': 'Jun',
        'Jul': 'Jul',
        'Aug': 'Ago',
        'Sep': 'Sep',
        'Oct': 'Oct',
        'Nov': 'Nov',
        'Dec': 'Dic'
    }
    for month in month_trans:
        date = re.sub(month, month_trans[month], date)
    return date


def play_beep():
    """ Plays an alert sound.
        It is used when a fatal error condition is found, o when the connection
        to TWS is broken and the program is restarted.
    """
    os.system('play -nq -t alsa synth 1 sine 180')


def check_date_validity(date):
    """
    Check if a string format is valid.

    PARAMETERS
    ----------
    date : str
        Date in string format: "YYYY-MM-DD'
    """
    year, month, day = date.split("-")
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        return False
    return True


def monday_and_friday(date):
    """
    Returns the monday and friday dates of the week containing base_date.
    
    Parameters
    ----------
    date : datetime.pyi

    Examples
    --------
    >>> str(monday_and_friday(datetime.datetime(2021, 11, 28)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'
    >>> str(monday_and_friday(datetime.datetime(2021, 11, 29)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'
    >>> str(monday_and_friday(datetime.datetime(2021, 11, 30)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'
    >>> str(monday_and_friday(datetime.datetime(2021, 12, 1)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'
    >>> str(monday_and_friday(datetime.datetime(2021, 12, 2)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'
    >>> str(monday_and_friday(datetime.datetime(2021, 12, 3)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'
    >>> str(monday_and_friday(datetime.datetime(2021, 12, 4)))
    '(datetime.datetime(2021, 11, 29), datetime.datetime(2021, 12, 3, 0, 0))'

    Returns
    -------
         (datetime.pyi, datetime.pyi)
         The required monday and friday dates.
    """
    day_of_week = date.weekday()
    if day_of_week == 6:
        day_of_week = -1
    monday = date - datetime.timedelta(days=day_of_week)
    friday = date + datetime.timedelta(days=4 - day_of_week)
    return monday, friday


def first_day_in_period(period, date):
    """
    Returns the base_date of the first day in period if 'base_date' is the last
    business day in period. Otherwise, it returns None. For instance, if the
    period is "daily" it returns 'base_date' if it is a business day, otherwise
    returns None. If period is "weekly" and 'base_date' is a friday it returns
    the previous monday base_date.
    If period is "monthly" and 'base_date' is the last business day in period
    then it returns the base_date of the first monday in the month.

    PARAMETERS
    ----------
    period : str
        Name of the period. It could be "daily", "weekly" or "monthly".
    date : datetime.pyi
        Date to be considered.

    RETURNS
    -------
        datetime.pyi
        The first base_date in the period ending in 'base_date'.

    EXAMPLES
    --------
    >>> first_day_in_period(
    ...    'monthly', datetime.datetime(2021, 10, 30))

    >>> first_day_in_period(
    ...    'weekly', datetime.datetime(2021, 5, 18))

    >>> first_day_in_period(
    ...    'weekly', datetime.datetime(2021, 7, 1))

    >>> first_day_in_period(
    ...    'daily', datetime.datetime(2021, 9, 19))

    >>> first_day_in_period(
    ...    'monthly', datetime.datetime(2021, 8, 16))

    >>> first_day_in_period(
    ...    'monthly', datetime.datetime(2021, 8, 31)).strftime("%Y%m%d")
    '20210802'
    >>> first_day_in_period(
    ...    'weekly', datetime.datetime(2021, 8, 20)).strftime("%Y%m%d")
    '20210816'
    >>> first_day_in_period(
    ...    'weekly', datetime.datetime(2021, 3, 23))

    >>> first_day_in_period(
    ...    'daily', datetime.datetime(2021, 8, 15))

    >>> first_day_in_period(
    ...    'daily', datetime.datetime(2021, 8, 16)).strftime("%Y%m%d")
    '20210816'
    """
    if date.weekday() > 4:
        return None
    if period == 'daily':
        return date
    if period == 'weekly':
        if date.weekday() == 4:
            return date + datetime.timedelta(days=-4)
        else:
            return None
    next_day = date
    while True:
        next_day += datetime.timedelta(days=1)
        if next_day.day > date.day and next_day.weekday() < 5:
            return None
        if next_day.day <= date.day:
            first_day = date
            first_day = first_day.replace(day=1)
            if first_day.weekday() < 5:
                return first_day
            if first_day.weekday() == 5:
                return first_day + datetime.timedelta(days=2)
            return first_day + datetime.timedelta(days=1)


def next_date(last_date, periodicity, day, time_):
    """
    From last base_date this method looks for the next base_date in which the
    time periodicity is met. For instance, if last_date where '2021-01-08' and
    the periodicity where 'monthly', the day 23, and the time_ 8:30 then the
    next base_date we are looking for would be '2021-01-23 08:30:00'. If it were
    '2021-01-24' then the next base_date would be '2021-02-23 08:30:00'.

    PARAMETERS
    ----------
    last_date : class datetime.datetime
        The last base_date.
    periodicity : str
        The time periodicity. Possible values are 'daily', 'weekly', 'monthly',
        'yearly', 'never'.
    day : integer
        Number of the day into the period selected:
        For 'daily it has no meaning.
        For 'weekly' it is the day of the week. (0-sunday, 1-monday and so on).
        For 'monthly' it is the day of the month (starting in 1).
        For 'yearly' ot is the day in the year (starting in 1).
    time_ : class datetime.datetime
        It is the hour.
    """
    if periodicity == 'never':
        return datetime.datetime(3000, 1, 1)
    # last base_date day for week
    ld_day_of_week = int(last_date.strftime("%w"))
    ld_day_of_year = int(last_date.strftime("%j"))
    if periodicity == 'daily':
        # Last base_date excess from start
        ld_offset = datetime.timedelta(hours=last_date.hour,
                                       minutes=last_date.minute,
                                       seconds=last_date.second)
        # excess from start for period
        p_offset = datetime.timedelta(hours=time_.hour,
                                      minutes=time_.minute,
                                      seconds=time_.second)
        result = last_date - ld_offset + p_offset
        if ld_offset >= p_offset:
            result = result + datetime.timedelta(days=1)
    elif periodicity == 'weekly':
        ld_offset = datetime.timedelta(days=ld_day_of_week,
                                       hours=last_date.hour,
                                       minutes=last_date.minute,
                                       seconds=last_date.second)
        p_offset = datetime.timedelta(days=day,
                                      hours=time_.hour,
                                      minutes=time_.minute,
                                      seconds=time_.second)
        result = last_date - ld_offset + p_offset
        if ld_offset >= p_offset:
            result = result + datetime.timedelta(days=7)
    elif periodicity == 'monthly':
        ld_offset = datetime.timedelta(days=last_date.day,
                                       hours=last_date.hour,
                                       minutes=last_date.minute,
                                       seconds=last_date.second)
        p_offset = datetime.timedelta(days=day,
                                      hours=time_.hour,
                                      minutes=time_.minute,
                                      seconds=time_.second)
        result = last_date - ld_offset + p_offset
        if ld_offset >= p_offset:
            year = result.year
            month = result.month
            day = result.day
            if month < 12:
                month += 1
            else:
                month = 1
                year += 1
            while not check_date_validity(
                    str(year) + '-' + str(month) + '-' + str(day)):
                day -= 1
            result = result.replace(year=year, month=month, day=day)
        elif day >= 28 and result.day <= 4:
            while result.day <= 4:
                result = result - datetime.timedelta(days=1)
    elif periodicity == 'yearly':
        ld_offset = datetime.timedelta(days=ld_day_of_year,
                                       hours=last_date.hour,
                                       minutes=last_date.minute,
                                       seconds=last_date.second)
        p_offset = datetime.timedelta(days=day,
                                      hours=time_.hour,
                                      minutes=time_.minute,
                                      seconds=time_.second)
        result = last_date - ld_offset + p_offset
        if ld_offset >= p_offset:
            result = result.replace(year=result.year + 1)
    else:
        raise ValueError("Wrong periodicity value: %s" % periodicity)

    return result


def get_answer(prompt):
    """
    Reads a user answer.

    Parameters
    ----------
    prompt : str
        Message displayed to the user.

    Returns
    -------
        str
        User's answer
    """
    return input(prompt)


def get_yes_no_answer(prompt):
    """
    Makes a question to the user and waits for a yes/no answer.

    PARAMETERS
    ----------
    prompt: str
        Questions to be asked to the user

    Returns
    -------
        str
        The 'yes' or 'no' answer. In lower case.
    """
    while True:
        answer = input(prompt).lower()
        if answer not in ['yes', 'no']:
            print("Answer 'yes' or 'no' please.")
            continue
        break
    return answer


def input_with_timeout(message, auto_response, timeout=60):
    """ Wait some time for a user answer. If it does not arrive after
    the timeout then an automatic response is yield.

    PARAMETERS
    ----------
    message : str
        Text displayed at standard output.
    auto_response : str
        Automatic response yield when the user did not answer anything.
    timeout : integer
        Seconds to wait before the automatic answer is generated.
    """
    print(message)
    user_response, _, _ = select.select([sys.stdin], [], [], timeout)
    if user_response:
        return sys.stdin.readline()
    print("Since you did not answer we assume f'{auto_response}'.")
    return auto_response


def incrementing_filename(base, ext):
    """
    Returns the string base+{cons}+'.'+extension of the next available filane in
    the file system where 'cons' is the lowest possible integer.
    Parameters
    ----------
    base : str
        First part of the file name.
    ext : str
        File name extension.

    Returns
    -------
        str
        The required file name.

    Examples
    --------
    >>> incrementing_filename('./pickle/20210104-20210212', 'pck')
    './pickle/20210104-20210212-1.pck'
    """
    ind = 1
    while True:
        file_name = base + '-' + str(ind) + '.' + ext
        if not os.path.exists(file_name):
            break
        ind += 1
    return file_name


class PendingWork:
    """
    Any method could use this procedure to store pending work information in
    some specific file into the './pending_work' directory. It is used when
    a program crashes to continue just in the point in which the crash
    occurred.
    """
    def __init__(self, file_name):
        """
        Returns a PendingWork class instance where the recover information
        will be saved into './pending_work/{file_name}

        PARAMETERS
        ----------
        file_name : str
            File to store the pending work.
        """
        ensure_path_existence("./pending_work/")
        self._file_name = file_name

    def write(self, data):
        """
        Stores recovery data.
        :param data: str
            Recovery data
        :return: None
        """
        with open('./pending_work/' + self._file_name, 'w') as f_out:
            f_out.write(data)

    def read(self):
        """
        Reads the recovery data.

        RETURNS
        -------
        None if the file does not exist, otherwise the recovery data.
        """
        if not path.exists('./pending_work/' + self._file_name):
            return None
        with open('./pending_work/' + self._file_name, 'r') as f_open:
            data = f_open.readline()
            if data != '' and data[-1] == '\n':
                data = data[:len(data) - 1]
        return data

    def clear(self):
        """
        Deletes the file associated to the class instance.
        :return: None
        """
        if path.exists('./pending_work/' + self._file_name):
            os.system('rm ' + './pending_work/' + self._file_name)
        else:
            raise FileExistsError("File " + './pending_work/' +
                                  self._file_name + " does not exist.")


def persistent_generate(elements, name):
    """
    This generator is used to download time series but the program is prone to
    crash, and it is a waste of time to start from the beginning. To allow
    recovery between crashes a PendingWork class instance is used.

    PARAMETERS
    ----------
    elements : list
        Elements to be generated (i.e. time series names).
    name : str
        File name of the PendingWork instance.
        Carefully avoid the use of the name of other PendingWork instance with
        the same name.
    """
    pending_work = PendingWork(name)
    initial_element = pending_work.read()
    for ind, element in enumerate(elements):
        if initial_element is not None and \
           not isinstance(initial_element, datetime.date) and \
           isinstance(element, datetime.date):
            initial_element = datetime.datetime.strptime(
                initial_element, "%Y-%m-%d %H:%M:%S")
        if initial_element is not None and initial_element != element:
            continue
        initial_element = None
        pending_work.write(str(element))
        yield ind, element
    pending_work.clear()


def ib_option_name(symbol, expire, strike, right):
    """
    Yields a string (using Interactive Brokers style) with the name of the
    option in the parameters.

    Parameters
    ----------
    symbol : str
        Option underlying.
    expire : datetime.pyi
        Expiration base_date.
    strike : float
        Option strike
    right : str
        Put ('P') or call ('C').

    Returns
    -------
        str
        An Interactive Brokers style text string with the option name.

    Examples
    --------
    >>> ib_option_name('ALB',datetime.datetime(2021, 2, 5),150.0,'C')
    'ALB 05FEB21 150.0 C'
    >>> ib_option_name('ALB',datetime.datetime(2021, 2, 19),150.0,'P')
    'ALB 19FEB21 150.0 P'
    >>> ib_option_name('D',datetime.datetime(2021, 2, 19),65.2,'C')
    'D 19FEB21 65.2 C'
    >>> ib_option_name('AAPL',datetime.datetime(2021, 10, 10),150.0,'P')
    'AAPL 10OCT21 150.0 P'
    """
    expire_str = expire.strftime("%d%b%y").upper().replace('ENE', 'JAN').\
        replace('ABR', 'APR').replace('AGO', 'AUG').\
        replace('DIC', 'DEC')
    symbol = symbol.replace('0', '').replace('1', '').replace('2', '').\
        replace('3', '').replace('4', '').replace('5', '').replace('6', '').\
        replace('7', '').replace('8', '').replace('9', '')
    return symbol + ' ' + expire_str + " " + "{0:.1f}".format(strike) + " " + \
        right


def from_standard_equity_option_convention(code: str) -> dict:
    """
    Transform a standard equity option convention code to record representation.

    Parameters
    ----------
    code : str
        Standard equity option convention code (see
        https://en.wikipedia.org/wiki/Option_naming_convention).

    Returns
    -------
        dict
        A dictionary containing:
        'symbol': Symbol name
        'expire': Option expiration base_date
        'right': Put (P) or Call (C).
        'strike': Option strike

    Examples:
    >>> from_standard_equity_option_convention('YHOO150416C00030000')
    {'symbol': 'YHOO', 'expire': '20150416', 'right': 'C', 'strike': 30.0}
    """
    option = dict()
    parts = re.search('([A-Z]+)([0-9]+)([CP])([0-9]+)', code)
    option['symbol'] = parts.group(1)
    expire = parts.group(2)
    option['expire'] = '20' + expire[0:2] + expire[2:4] + expire[4:6]
    option['right'] = parts.group(3)
    option['strike'] = float(parts.group(4)) / 1000.0
    return option
