from typing import Callable, Tuple, List
import sqlite3
import numpy as np
import pandas as pd

from .defs import *

class Data:
    def __init__(self, db_file: str) -> None:
        self._isLoaded = False
        self._agg = None
        self.db_file = db_file
    
    def __del__(self) -> None:
        self.unload()
        del self._agg

    def load(self) -> None:
        try:
            con = sqlite3.connect(self.db_file)
            self._clients =\
                pd.read_sql_query("SELECT * FROM client_by_id", con)
            self._queries =\
                pd.read_sql_query("SELECT * FROM query_storage", con)
            self._queries['time'] =\
                pd.to_datetime(self._queries['timestamp'], unit='s')
        except sqlite3.Error as e:
            print(f"Sqlite3 error: {e.args[0]}")
        except Exception as e:
            print("Unexpected error: {e.args[0]}")
        else:
            self._isLoaded = True
        finally:
            con.close()

    def allClients(self) -> List[str]:
        if not self._isLoaded:
            self.load()
        return self._clients['ip'].tolist()

    def allStatuses(self) -> List[str]:
        if not self._isLoaded:
            self.load()
        return list(status_help.keys())

    def allTypes(self) -> List[str]:
        if not self._isLoaded:
            self.load()
        return [query_lookup[t] for t in self._queries['type'].unique().tolist()]

    def unload(self) -> None:
        del self._clients
        del self._queries
        self._isLoaded = False

    def aggregate(self, select: Callable[[pd.DataFrame, pd.DataFrame], Tuple[np.ndarray, np.ndarray]]) -> None:
        if not self._isLoaded:
            self.load()
        self._agg = select(self._clients, self._queries)

    @property
    def agg(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._agg


class QueryData(Data):
    def filter(self, ip_addrs: List[str], statuses: List[int] = range(15), types: List[int] = range(17), nbins: int = 500) -> None:
        def select(clients: pd.DataFrame, queries: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
            client_ids = clients[clients['ip'].isin(ip_addrs)]['id']
            mask = (queries['status'].isin(statuses) & queries['type'].isin(
                types) & queries['client'].isin(client_ids))
            cnt, bn = np.histogram(queries[mask]['timestamp'], bins=nbins)
            return pd.to_datetime(0.5 * (bn[1:] + bn[:-1]), unit='s'), cnt
        self.aggregate(select)
