import selenium
from selenium import webdriver
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

    LOAD_SLEEP = 20

    def __init__(self):
        self.driver = webdriver.Chrome("G:\projects\chromedriver")
        WebDriverWait(self.driver, self.LOAD_SLEEP).until(EC.url_changes(self.driver.get(self.LAUNDRY_URL)))

        prefered_times = [2, 3, 4, 5, 6, 7]

    def read_in_credentials(self):
        credentials = open('credentials.txt', 'r')
        self.user = credentials.read()
        self.password = credentials.read()

    def login(self):
        user_input = self.find_element_by_xpath(
            "/html/body/main/div[3]/div/div[2]/article/div/div/section[1]/form/section/input[1]")
        user_input.send_keys(self.user)

        password_input = self.find_element_by_xpath(
            "/html/body/main/div[3]/div/div[2]/article/div/div/section[1]/form/section/input[2]")
        password_input.send_keys(self.password)

        btn_login = self.find_element_by_xpath(
            "/ html / body / main / div[3] / div / div[2] / article / div / div / section[1] / form / section / button")
        btn_login.click()

    def open_booking(self):
        btn_get_laundry_house = self.find_element_by_xpath(
            "/html/body/main/div[2]/div/div[2]/article/div/div/div/button")
        btn_get_laundry_house.click()

        time.sleep(self.LOAD_SLEEP)

        btn_get_booking = self.find_element_by_xpath(
            "/html/body/main/div[2]/div/div[2]/article/div/div/div/div[2]/ul/li/a")
        btn_get_booking.click()

    def choose_laundry_house(self, house):
        btn_select_house = self.find_element_by_xpath(self.LAUNDRY_HOUSES[house])
        btn_select_house.click()

    def get_avaible_times(self):
        print("These times are available today :)")

    def login_and_book_weekend(self):
        time.sleep(self.LOAD_SLEEP)

        self.login()

        time.sleep(self.LOAD_SLEEP)

        self.open_booking()

        time.sleep(self.LOAD_SLEEP)

        self.base_window = self.driver.window_handles[0]
        self.booking_window = self.driver.window_handles[1]
        self.driver.switch_to.window(self.booking_window)

        self.choose_laundry_house('17')

        time.sleep(self.LOAD_SLEEP)
        days = [self.book_saturday([2, 3, 4, 5, 6, 7])]
        booked = False
        for day in days:
            if day():
                return True

    def book_saturday(self, prefered_times):

        for l_time in prefered_times:
            if self.time_is_free(5, l_time):
                self.book_time(5, l_time)
                return True
        return False

    def get_current_day(self):
        days = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']
        day_number = datetime.datetime.today().weekday()
        return days[day_number]

    def book_time(self, weekday_index: int, time_index: int):  # 5 1
        xpath_to_time = self.get_xpath_from_datetime(weekday_index, time_index)
        booking_btn = self.find_element_by_xpath(xpath_to_time)
        booking_btn.click()

    def get_booking_status(self, weekday_index, time_index):
        xpath = self.get_xpath_from_datetime(weekday_index, time_index)
        return self.driver.find_element_by_xpath(xpath + '/a').text

    def time_is_free(self, weekday_index, time_index):
        free_status = 'Ledig'
        status = self.get_booking_status(weekday_index, time_index)
        return free_status == status

    def time_is_mine(self, weekday_index, time_index):
        my_time = 'Min tid'
        status = self.get_booking_status(weekday_index, time_index)
        return my_time == status

    def time_is_booked(self, weekday_index, time_index):
        bokad = 'Bokad'
        status = self.get_booking_status(weekday_index, time_index)
        return bokad == status

    def shift_day_index(self, day, shift):
        return ((day - shift) % 7) + 1

    def get_xpath_from_datetime(self, weekday_index, time_index):
        today_index = datetime.datetime.today().weekday()
        shifted_date = self.shift_day_index(weekday_index, today_index)
        return self.laundry_time_xpath_base.format(shifted_date, time_index)

    def have_booking(self):
        is_booked_btn = self.find_element_by_xpath('/html/body/form/div[5]/div[1]/dl/dd[2]/a')
        if 'Avboka' in is_booked_btn.text:
            return self.find_element_by_xpath('/html/body/form/div[5]/div[1]/dl/dd[1]').text
        print("No current booking")
        return False

    def unbook_current_time(self):
        if self.have_booking():
            is_booked_btn = self.find_element_by_xpath('/html/body/form/div[5]/div[1]/dl/dd[2]/a')
            is_booked_btn.click()

    def find_element_by_xpath(self, xpath):
        try:
            return self.driver.find_element_by_xpath(xpath)
        except selenium.common.exceptions.NoSuchElementException:
            print("Element not found")
            return False

    def logout(self):
        """ Log out from Stockholmshem """
