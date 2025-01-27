###############################################################################
#
# Copyright 2020, University of Stuttgart: Institute for Natural Language Processing (IMS)
#
# This file is part of Adviser.
# Adviser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3.
#
# Adviser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adviser.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################


import re
import json
import math
import os
import sqlite3
from io import StringIO
from typing import List, Iterable

from utils.domain import Domain

from geopy.geocoders import Nominatim
import geopy.distance


class JSONLookupDomain(Domain):
    """ Abstract class for linking a domain based on a JSON-ontology with a database
       access method (sqllite).
    """

    def __init__(self, name: str, json_ontology_file: str = None, sqllite_db_file: str = None, \
                 display_name: str = None):
        """ Loads the ontology from a json file and the data from a sqllite
            database.

            To create a new domain using this format, inherit from this class
            and overwrite the _get_domain_name_()-method to return your
            domain's name.

        Arguments:
            name (str): the domain's name used as an identifier
            json_ontology_file (str): relative path to the ontology file
                                (from the top-level adviser directory, e.g. resources/ontologies)
            sqllite_db_file (str): relative path to the database file
                                (from the top-level adviser directory, e.g. resources/databases)
            display_name (str): the domain's name as it appears on the screen
                                (e.g. containing whitespaces)
        """
        super(JSONLookupDomain, self).__init__(name)

        root_dir = self._get_root_dir()
        self.sqllite_db_file = sqllite_db_file
        # make sure to set default values in case of None
        json_ontology_file = json_ontology_file or os.path.join('resources', 'ontologies',
                                                                name + '.json')
        sqllite_db_file = sqllite_db_file or os.path.join('resources', 'databases',
                                                          name + '.db')

        self.ontology_json = json.load(open(root_dir + '/' + json_ontology_file))
        # load database
        self.db = self._load_db_to_memory(root_dir + '/' + sqllite_db_file)

        self.display_name = display_name if display_name is not None else name

    def __getstate__(self):
        # remove sql connection from state dict so that pickling works
        state = self.__dict__.copy()
        if 'db' in state:
            del state['db']
        return state

    def _get_root_dir(self):
        """ Returns the path to the root directory """
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _sqllite_dict_factory(self, cursor, row):
        """ Convert sqllite row into a dictionary """
        row_dict = {}
        for col_idx, col in enumerate(cursor.description):
            # iterate over all columns, get corresponding db value from row
            row_dict[col[0]] = row[col_idx]
        return row_dict

    def _load_db_to_memory(self, db_file_path : str):
        """ Loads a sqllite3 database from file to memory in order to save
            I/O operations

        Args:
            db_file_path (str): absolute path to database file

        Returns:
            A sqllite3 connection
        """

        # open and read db file to temporary file
        file_db = sqlite3.connect(db_file_path, check_same_thread=False)
        tempfile = StringIO()
        for line in file_db.iterdump():
            tempfile.write('%s\n' % line)
        file_db.close()
        tempfile.seek(0)
        # Create a database in memory and import from temporary file
        db = sqlite3.connect(':memory:', check_same_thread=False)
        db.row_factory = self._sqllite_dict_factory
        db.cursor().executescript(tempfile.read())
        db.commit()
        # file_db.backup(databases[domain]) # works only in python >= 3.7

        return db

    def find_entities(self, constraints: dict, requested_slots: Iterable = iter(())):
        """ Returns all entities from the data backend that meet the constraints, with values for
            the primary key and the system requestable slots (and optional slots, specifyable
            via requested_slots).

        Args:
            constraints (dict): Slot-value mapping of constraints.
                                If empty, all entities in the database will be returned.
            requested_slots (Iterable): list of slots that should be returned in addition to the
                                        system requestable slots and the primary key

        """
        # values for name and all system requestable slots
        select_clause = ", ".join(set([self.get_primary_key()]) |
                                  set(self.get_system_requestable_slots()) |
                                  set(requested_slots))
        query = "SELECT {} FROM {}".format(select_clause, self.get_domain_name())
        try:
            constraints = {slot: value.replace("'", "''") for slot, value in constraints.items()
                        if value is not None and str(value).lower() != 'dontcare'}
        except AttributeError:
            constraints = {slot: [value.replace("'", "''") for value in values if value is not None and str(value).lower() != 'dontcare'] for slot, values in constraints.items()}
        if constraints:
            if all(isinstance(v, list) for v in constraints.values()):
                for i, (key, vals) in enumerate(constraints.items()):
                    if len(vals) == 0:
                        continue
                    if not 'WHERE' in query:
                        query += ' WHERE ('
                    else:
                        query += ') AND ('
                    query += ' OR '.join("{}='{}' COLLATE NOCASE".format(key, str(val)) for val in vals)
                query += ')'
            else:
                query += ' WHERE ' + ' AND '.join("{}='{}' COLLATE NOCASE".format(key, str(val))
                                              for key, val in constraints.items())
        return self.query_db(query)

    def find_info_about_entity(self, entity_id, requested_slots: Iterable):
        """ Returns the values (stored in the data backend) of the specified slots for the
            specified entity.

        Args:
            entity_id (str): primary key value of the entity
            requested_slots (dict): slot-value mapping of constraints

        """
        if requested_slots:
            select_clause = ", ".join(sorted(requested_slots))
        # If the user hasn't specified any slots we don't know what they want so we give everything
        else:
            select_clause = "*"
        query = 'SELECT {} FROM {} WHERE {}="{}";'.format(
            select_clause, self.get_domain_name(), self.get_primary_key(), entity_id)
        return self.query_db(query)

    def query_db(self, query_str):
        """ Function for querying the sqlite3 db

        Args:
            query_str (string): sqlite3 query style string

        Return:
            (iterable): rows of the query response set
        """
        if "db" not in self.__dict__:
            root_dir = self._get_root_dir()
            sqllite_db_file = self.sqllite_db_file or os.path.join(
                'resources', 'databases', self.name + '.db')
            self.db = self._load_db_to_memory(root_dir + '/' + sqllite_db_file)
        cursor = self.db.cursor()
        cursor.execute(query_str)
        res = cursor.fetchall()
        return res
    
    def query_opening_info(self, req_openingday: str, name: str):
        """Query the database for opening hours and extract information for the requested day

        Args:
            req_openingday (str): requested day by the user
            name (str): name of the restaurant

        Returns:
            str: opening information
        """
        opening_hours = self.query_db(f'SELECT opening_hours FROM {self.get_domain_name()} WHERE name="{name}"')[0]['opening_hours']
        opening_hours = json.loads(opening_hours)
        opening_info = opening_hours[req_openingday]
        if opening_info == 'Closed':
            opening_info = 'is closed'
        else:
            opening_info = 'has opened from ' + opening_info
        return opening_info
    
    def query_manner_info(self, req_manner: str, name: str):
        """Query the database for manners and extract information for the requested manner

        Args:
            req_manner (str): requested manner by the user
            name (str): name of the restaurant

        Returns:
            str: manner information
        """
        manner = self.query_db(f'SELECT manner FROM {self.get_domain_name()} WHERE name="{name}"')[0]['manner']
        manner = json.loads(manner)
        manner_info = 'Sorry, this information is not available for'
        for m in manner:
            if req_manner in m:
                if 'No' in m:
                    manner_info = f'Sorry, {req_manner} is not offered by'
                else:
                    manner_info = f'Yes, {req_manner} is offered by'
            if ('pickup' in m or 'drive-through' in m) and req_manner == 'takeaway':
                manner_info = f'Yes, {req_manner} is offered by'
        return manner_info
    
    def modify_db(self, modify_str: str):
        """Function for mofiying a sqlite3 db

        Args:
            modify_str (str): sqlite3 update style string
        """
        if "db" not in self.__dict__:
            root_dir = self._get_root_dir()
            sqllite_db_file = self.sqllite_db_file or os.path.join(
                'resources', 'databases', self.name + '.db')
            self.db = self._load_db_to_memory(root_dir + '/' + sqllite_db_file)
        cursor = self.db.cursor()
        cursor.execute(modify_str)

    def enter_rating(self, given_rating: float, name: str):
        """Compute the nwe rating given the current rating, number of reviews and the given rating and update the db

        Args:
            given_rating (float): rating given by the user
            name (str): name of the restaurant/bar
        """
        rating_num = self.query_db(f'SELECT rating, num_reviews FROM {self.get_domain_name()} WHERE name="{name}"')[0]
        current_rating = float(rating_num['rating'])
        num_reviews = int((rating_num['num_reviews']).replace(',', ''))
        #num_reviews = int((rating_num['num_reviews']))
        #print("(jslookup) rating_num:", rating_num, "current_rating:", current_rating, "num_reviews:", num_reviews)

        new_rating = ((current_rating * num_reviews) + given_rating) / (num_reviews + 1)
        new_rating = str(round(new_rating, 1))
        #print("(jslookup) new_rating:", new_rating)
        modify_str = f'UPDATE {self.get_domain_name()} SET rating="{new_rating}" WHERE name="{name}"'
        self.modify_db(modify_str)

    def enter_review(self, review: str, name: str):
        """Add new review to the existing reviews and update the db

        Args:
            review (str): the given review
            name (str): name of the restaurant/bar
        """
        reviews = self.query_db(f'SELECT reviews FROM {self.get_domain_name()} WHERE name="{name}"')[0]['reviews']
        reviews = reviews.replace("'s", "’s")
        reviews = reviews.replace("'", "\"")
        #reviews = reviews.replace("'", "’")
        reviews = json.loads(reviews)
        reviews.append(review)
        reviews = str(reviews)
        modify_str = f'UPDATE {self.get_domain_name()} SET reviews="{reviews}" WHERE name="{name}"'
        self.modify_db(modify_str)
    
    def distance_duration(self, start_point: str, name: str, distance_manner: str):
        """Calcualtes the distance and approximates the duration by bike between the start point and the address of the restaurant

        Args:
            start_point (str): given start point
            name (str): name of the restaurant

        Returns:
            str, str: distance, duration
        """
        uni_pattern = re.compile("((i am )?at (the )?)?(uni|school|university|uni stuttgart|university of stuttgart)$")
        schwabstr_pattern = re.compile("((i am )?at (the )?)?(schwabstr|schwabstraße|schwabstrasse)$")
        hbf_pattern = re.compile("((i am )?at (the )?)?(stuttgart )?(hauptbahnhof|main station|central station|hbf|haupt( )?bf)$")

        address = self.query_db(f'SELECT address FROM {self.get_domain_name()} WHERE name="{name}"')[0]['address']
        if (uni_pattern.match(start_point)==None)==False:
            start_point = 'Pfaffenwaldring 5, 70569 Stuttgart'
        if (hbf_pattern.match(start_point)==None)==False:
            start_point = 'Arnulf-Klett-Platz 2, 70173 Stuttgart'
        if (schwabstr_pattern.match(start_point)==None)==False:
            start_point = 'Schwabstraße 43, 70197 Stuttgart'
        locator = Nominatim(user_agent="myGeocoder")
        address_loc = locator.geocode(address)
        try:
            address_coordinates = (address_loc.latitude, address_loc.longitude)
        except AttributeError:
            address_coordinates = None
        start_point_loc = locator.geocode(start_point)
        try:
            start_point_coordinates = (start_point_loc.latitude, start_point_loc.longitude)
        except AttributeError:
            start_point_coordinates = None
        if address_coordinates is None or start_point_coordinates is None:
            return None, None
        distance = geopy.distance.geodesic(start_point_coordinates, address_coordinates).km
        if distance_manner == 'by foot':
            # assumed by foot with average speed 6 km/h
            duration = math.ceil(10*distance)
            if int(duration) < 60:
                duration_out = str(duration) + ' minutes'
            if int(duration) >= 60:
                duration_out = "%d:%02d"%(duration//60, duration%60) +' hour'
            distance = str(round(distance, 2)) + ' km'
        elif distance_manner == 'by bike':
            # assumed by bike with average speed 21 km/h = 0.35 km/min
            if distance/21 > 1:
                duration = math.ceil(distance/21)
            else:
                duration = math.ceil(distance/0.35)
            if int(duration) < 60:
                duration_out = str(duration) + ' minutes'
            if int(duration) >= 60:
                duration_out = "%d:%02d"%(duration//60, duration%60) +' hour'
            distance = str(round(distance, 2)) + ' km'

        elif distance_manner == 'by car':
            # assumed by car with average speed 30 km/h = 0.5 km/min
            if (distance/30) > 1:
                duration = math.ceil(distance/30)
            else:
                duration = math.ceil(distance/0.5)
            if int(duration) < 60:
                duration_out = str(duration) + ' minutes'
            if int(duration) >= 60:
                duration_out = "%d:%02d"%(duration//60, duration%60) +' hour'
            distance = str(round(distance, 2)) + ' km'
        # if int(duration) < 60:
        #     duration_out = str(duration) + ' minutes'
        # if int(duration) >= 60:
        #     duration_out = "%d:%02d"%(duration//60, duration%60) +' hour'
        # distance = str(round(distance, 2)) + ' km'
        else:
            distance = 'BadTravelManner'
            duration_out = 'BadTravelManner'
        return distance, duration_out

    def get_display_name(self):
        return self.display_name

    def get_requestable_slots(self) -> List[str]:
        """ Returns a list of all slots requestable by the user. """
        return self.ontology_json['requestable']

    def get_system_requestable_slots(self) -> List[str]:
        """ Returns a list of all slots requestable by the system. """
        return self.ontology_json['system_requestable']

    def get_informable_slots(self) -> List[str]:
        """ Returns a list of all informable slots. """
        return self.ontology_json['informable'].keys()

    def get_possible_values(self, slot: str) -> List[str]:
        """ Returns all possible values for an informable slot

        Args:
            slot (str): name of the slot

        Returns:
            a list of strings, each string representing one possible value for
            the specified slot.
         """
        return self.ontology_json['informable'][slot]
    
    def get_givable_ratings(self) -> List[str]:
        """Returns all possible values for giving ratings

        Returns:
            List[str]: givable ratings
        """
        return self.ontology_json['ratings_givable']

    def get_opening_days(self) -> List[str]:
        return self.ontology_json['opening_day']
    
    def get_manner(self) -> List[str]:
        return self.ontology_json['manner']

    def get_primary_key(self):
        """ Returns the name of a column in the associated database which can be used to uniquely
            distinguish between database entities.
            Could be e.g. the name of a restaurant, an ID, ... """
        return self.ontology_json['key']


    def get_pronouns(self, slot):
        if slot in self.ontology_json['pronoun_map']:
            return self.ontology_json['pronoun_map'][slot]
        else:
            return []

    def get_keyword(self):
        if "keyword" in self.ontology_json:
            return self.ontology_json['keyword']

    # negative inform
    def get_negativeinformable_slots(self) -> List[str]:
        return self.ontology_json['negative_informable'].keys()

    def get_negativeinform_possible_values(self, slot: str) -> List[str]:
        return self.ontology_json['negative_informable'][slot]