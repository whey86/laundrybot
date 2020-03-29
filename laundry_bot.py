import selenium
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime


class LaundryBot:
    LAUNDRY_URL = "https://www.stockholmshem.se/logga-in/?returnUrl=/mina-sidor/boka-tvattid/"

    HOUSE_BASE_URL = '/html/body/form/div[5]/div[2]/div[1]/ul/li[{}]/a'

    LAUNDRY_HOUSES = {
        '35B': HOUSE_BASE_URL.format('1'),
        '53': HOUSE_BASE_URL.format('2'),
        '17': HOUSE_BASE_URL.format('3')
    }

    laundry_time_xpath_base = '/html/body/form/div[5]/div[2]/div[3]/div/div[{}]/div[{}]/dl/dd[1]'

    DAYS = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']

    LOAD_SLEEP = 30

    def __init__(self):
        self.driver = webdriver.Chrome("G:\projects\chromedriver")
        WebDriverWait(self.driver, self.LOAD_SLEEP).until(EC.url_changes(self.driver.get(self.LAUNDRY_URL)))
        credentials = open('credentials.txt', 'r')
        self.user = credentials.readline().strip()
        self.password = credentials.readline().strip()

        self.prefered_times = [2, 3, 4, 5, 6]

    def login_and_book_weekend(self):
        self._login()

        self._open_booking()

        self.base_window = self.driver.window_handles[0]
        self.booking_window = self.driver.window_handles[1]
        self.driver.switch_to.window(self.booking_window)

        self._choose_laundry_house('17')

        if self.have_booking():
            print("Booking exist")
            return True

        days = [self._book_saturday, self.book_sunday]
        for day in days:
            if day(self.prefered_times):
                return True
        return False

    def login_and_get_booking(self):
        self._login()
        self._open_booking()
        self.base_window = self.driver.window_handles[0]
        self.booking_window = self.driver.window_handles[1]
        self.driver.switch_to.window(self.booking_window)
        self._choose_laundry_house('17')
        return self.have_booking()

    def get_avaible_times(self):
        print("These times are available today :)")

    def have_booking(self):
        is_booked_xpath = '/html/body/form/div[5]/div[1]/dl/dd[2]/a'

        is_booked_btn = self._find_element_by_xpath(is_booked_xpath)

        booked_time_text = None

        # booking found
        if is_booked_btn:
            booked_xpath = '/html/body/form/div[5]/div[1]/dl/dd[1]'
            booked_time_field = self._wait_and_select_element_by_xpath(booked_xpath)
            booked_time_text = booked_time_field.text
            print(booked_time_text)
        else:
            print("No booking")
        return booked_time_text

    def _login(self):
        user_input_xpath = "/html/body/main/div[3]/div/div[2]/article/div/div/section[1]/form/section/input[1]"
        user_password_xpath = "/html/body/main/div[3]/div/div[2]/article/div/div/section[1]/form/section/input[2]"
        login_xpath = "/html/body/main/div[3]/div/div[2]/article/div/div/section[1]/form/section/button"

        # wait on elements to load
        user_input = self._wait_and_select_element_by_xpath(user_input_xpath)
        password_input = self._wait_and_select_element_by_xpath(user_password_xpath)
        btn_login = self._wait_and_select_element_by_xpath(login_xpath)

        # input credentials
        user_input.send_keys(self.user)
        password_input.send_keys(self.password)

        # login
        btn_login.click()

    def _open_booking(self):

        # xpaths
        btn_laundry_house = "/html/body/main/div[2]/div/div[2]/article/div/div/div/button"
        btn_booking = "/html/body/main/div[2]/div/div[2]/article/div/div/div/div[2]/ul/li/a"

        # wait on element
        btn_get_laundry_house = self._wait_and_select_element_by_xpath(btn_laundry_house)

        # enter laundry house
        btn_get_laundry_house.click()

        # wait on element
        btn_get_booking = self._wait_and_select_element_by_xpath(btn_booking)

        # enter booking site
        btn_get_booking.click()

    def _choose_laundry_house(self, house):
        btn_select_house = self._wait_and_select_element_by_xpath(self.LAUNDRY_HOUSES[house])
        btn_select_house.click()

    def _book_day(self, day, prefered_times):
        for l_time in prefered_times:
            if self._time_is_free(day, l_time):
                self._book_time(day, l_time)
                return True
        return False

    def _book_saturday(self, prefered_times):
        return self._book_day(5, prefered_times)

    def book_sunday(self, prefered_times):
        return self._book_day(6, prefered_times)

    def get_current_day(self):
        day_number = datetime.datetime.today().weekday()
        today = self.DAYS[day_number]
        return today

    def _book_time(self, weekday_index: int, time_index: int):  # 5 1
        xpath_to_time = self._get_xpath_from_datetime(weekday_index, time_index)
        booking_btn = self._wait_and_select_element_by_xpath(xpath_to_time)
        booking_btn.click()

    def _get_booking_status(self, weekday_index, time_index):
        xpath = self._get_xpath_from_datetime(weekday_index, time_index)
        status_text = None

        if self.driver.find_elements(By.XPATH(xpath + '/a')).__sizeof__() != 0:
            status = self._wait_and_select_element_by_xpath(xpath + '/a')
        elif self.driver.find_elements(By.XPATH(xpath + '/span')).__sizeof__() != 0:
            status = self._wait_and_select_element_by_xpath(xpath + '/span')

        if status:
            status_text = status.text
        return status_text

    def _time_is_free(self, weekday_index, time_index):
        free_status = 'Ledig'
        status = self._get_booking_status(weekday_index, time_index)
        return free_status == status

    def _time_is_mine(self, weekday_index, time_index):
        my_time = 'Min tid'
        status = self._get_booking_status(weekday_index, time_index)
        return my_time == status

    def _time_is_booked(self, weekday_index, time_index):
        bokad = 'Bokad'
        status = self._get_booking_status(weekday_index, time_index)
        return bokad == status

    def _shift_day_index(self, day, shift):
        return ((day - shift) % 7) + 1

    def _get_xpath_from_datetime(self, weekday_index, time_index):
        today_index = datetime.datetime.today().weekday()
        shifted_date = self._shift_day_index(weekday_index, today_index)
        print(shifted_date)
        return self.laundry_time_xpath_base.format(shifted_date, time_index)

    def _unbook_current_time(self):
        if self.have_booking():
            is_booked_xpath = '/html/body/form/div[5]/div[1]/dl/dd[2]/a'
            is_booked_btn = self._wait_and_select_element_by_xpath(is_booked_xpath)
            is_booked_btn.click()

    def _find_element_by_xpath(self, xpath):
        try:
            return self.driver.find_element_by_xpath(xpath)
        except selenium.common.exceptions.NoSuchElementException:
            print("Element not found")
            return False

    def _wait_and_select_element_by_xpath(self, xpath_id):
        time.sleep(5)
        element = None
        try:
            element = WebDriverWait(self.driver, self.LOAD_SLEEP).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath_id)))[0]
        except selenium.common.exceptions.TimeoutException as e:
            print(e)
            pass
        return element

    def logout(self):
        """ Logs out from booking """
        logout = self._find_element_by_xpath('/html/body/form/div[5]/p/a')
        logout.click()

    def close(self):
        """ close browser """
        self.driver.quit()
