from pymongo import MongoClient
from models.model_domain import *
from datetime import datetime
import os
from storage.database import Database

def create_domain(_domain_name, _monitor, _crawl_freq):
    try:
        domain = Domain(
            domain=_domain_name,
            register_date=datetime.now(),
            monitor=_monitor,
            crawl_freq = _crawl_freq
        )
        domain.save()
        print(f"Domain {_domain_name} saved with ID: {domain.id}")
    except Exception as e:
        print(f"Error saving domain: {e}")


def find_domain(domain_name):
    try:
        domain = Domain.objects(domain=domain_name).first()
        if domain:
            print(f"Found domain: {domain.domain}, Last Crawl: {domain.last_crawl}, Crawl Frequency: {domain.crawl_freq}")
        else:
            print("Domain not found.")
    except Exception as e:
        print(f"Error finding domain: {e}")