import sqlite3
import os
import json
import inspect
from datetime import datetime

class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)

@Singleton
class DBLogSingleton(object):

    insert = "INSERT INTO Logs (level, class_name, method_name, error_message, created_at ) VALUES (?, ?, ?, ?, ?);"

    def __init__(self):
        with open("config/config.json", "r") as file:
            is_new = False
            config = json.load(file)
            try:
                db_location = config["log_db_location"]
                db_name = config["log_db_name"]
            except KeyError as e:
                return
            db_path = os.path.join(db_location, db_name)
            if not os.path.isfile(db_path):
                file = open(db_path, "w")
                file.close()
                is_new = True

            self.__db = sqlite3.connect(database=db_path, timeout=10)

            if is_new:
                with open("data/DBVersion/log.sql") as log_script:
                    script = log_script.read()
                    self.__db.executescript(script)

    def __del__(self):
        self.close()

    def close(self):
        self.__db.close()

    def DEBUG(self, class_name, method_name, error_message, created_at):
        self.__db.execute(self.insert, ("DEBUG", class_name, method_name, str(error_message), str(created_at)))
        self.__db.commit()

    def WARNING(self, class_name, method_name, error_message, created_at):
        self.__db.execute(self.insert, ("WARNING", class_name, method_name, str(error_message), str(created_at)))
        self.__db.commit()

    def ERROR(self, class_name, method_name, error_message, created_at):
        self.__db.execute(self.insert, ("ERROR", class_name, method_name, str(error_message), str(created_at)))
        self.__db.commit()

@Singleton
class DBHelperSingleton(object):
    current_version = 1

    def __init__(self):
        with open("config/config.json", "r+") as file:
            config = json.load(file)
            try:
                db_location = config["db_location"]
                db_name = config["db_name"]
                db_version = config["db_version"]
                db_new_version = config["db_new_version"]
            except KeyError as error:
                DBLogSingleton.instance().ERROR(self.__class__.__name__, inspect.currentframe().f_code.co_name, error,
                                                datetime.now())
                return
            db_path = os.path.join(db_location, db_name)
            if not os.path.isfile(db_path):
                dbfile = open(db_path, "w")
                dbfile.close()

            self.__db = sqlite3.connect(database=db_path, timeout=10)
            if db_version < db_new_version:
                self.__on_update(db_version, db_new_version)
                config["db_version"] = db_new_version

    def __del__(self):
        self.close()

    def close(self):
        self.__db.close()

    def __on_update(self, current, new):
        for version in range(current + 1, new + 1):
            match version:
                case 1:
                    with open("data/DBVersion/1.sql","r") as script_file:
                        try:
                            script = script_file.read()
                            self.__db.executescript(script)
                        except IOError as error:
                            DBLogSingleton.instance().ERROR(self.__class__.__name__,
                                                            inspect.currentframe().f_code.co_name,
                                                            error, datetime.now())
                            return False
                        except sqlite3.OperationalError as error:
                            DBLogSingleton.instance().ERROR(self.__class__.__name__,
                                                            inspect.currentframe().f_code.co_name, error,
                                                            datetime.now())
                            return False

        return True



