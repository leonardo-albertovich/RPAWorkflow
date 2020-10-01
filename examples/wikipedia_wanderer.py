import argparse
import random
import RPAWorkflow
import time
import sys

from selenium import webdriver
from selenium.common.exceptions import *

from RPAWorkflow import BrowserHandler, RuleSet, Rule
from RPAWorkflow.constants import *
from RPAWorkflow.decorators import *
from RPAWorkflow.modifiers import *
from RPAWorkflow.actions import *


class DummyTestHandler(RPAWorkflow.BrowserHandler):
    @document_handler(Priority.HIGHEST, modifiers=[ContinueEvaluating])
    def random_delay(self):
        print('A random delay is inserted for each request if desired')

        time.sleep(random.uniform(0.5, 3))

    @document_handler(Priority.HIGH, [RuleSet(Rule('/wiki/Main_Page', PlainText, CaseLess, Mandatory, Url))], invocation_limit=1)
    def landing_page_handler(self):
        print('Landing page detected, searching : %s' % (self.context['initial_search_term']))

        search_box = self.backend.find_element_by_name('search')
        search_box.send_keys(self.context['initial_search_term'])
        search_box.submit()


    @document_handler(Priority.LOW, modifiers=[ContinueEvaluating])
    def handle_page(self):
        print('Content page detected, jumping to a random page!')

        link_clicked_successfully = False

        for retry_counter in range(5):
            try:
                links = self.backend.find_elements_by_partial_link_text('')
                links[random.randint(0, len(links)-1)].click()

                # If the selected link could be clicked just continue
                link_clicked_successfully = True

                break

            except ElementNotInteractableException:
                pass

        if not link_clicked_successfully:
            print('Going back since we could not click a random link in this page (could be a media element or something)')

            self.backend.execute_script("window.history.go(-1)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('initial_search_term', type=str, help='The term that will be searched once we hit wikipedias landing page')

    args = parser.parse_args()

    context =   {
                    'initial_search_term' : args.initial_search_term
                }

    driver = webdriver.Chrome('chromedriver.exe')

    driver.get('https://en.wikipedia.org/');

    workflow = DummyTestHandler(driver, context)

    workflow.dispatch_while_working()

    try:
        print('PRESS CTRL+C TO CLOSE THE WEB BROWSER')

        while True:
            time.sleep(1)

    except KeyboardInterrupt as ex:
        pass

    driver.quit()
