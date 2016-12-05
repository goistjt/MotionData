'''
Created on Oct 31, 2016

@author: yangr
'''
from flask_master.data_analysis import data_analysis as da
from flask_master.database import crud_class

def main():
    crud = crud_class.Crud()
    session_id = 0
    session_records = crud.getAllRecordsFromSession(session_id)[0][0]
    records = crud.getRecord_data(session_records)
    print(records)

if __name__ == '__main__':
    main()