import os
import shutil
import sqlite3
import pandas as pd

# This is what we use for the testing in the project.
local_file = "../travel_new.sqlite"

# This is the backup file, it allows up to re-start during testing.
backup_file = "../travel2.sqlite"


def update_dates():
    """
    更新数据库中的日期，使其与当前时间对齐。

    参数:
        file (str): 要更新的数据库文件路径。

    返回:
        str: 更新后的数据库文件路径。
    """
    # 使用备份文件覆盖现有文件，作为重置步骤
    shutil.copy(backup_file, local_file)  # 如果目标路径已经存在一个同名文件，shutil.copy 会覆盖该文件。

    conn = sqlite3.connect(local_file)
    # cursor = conn.cursor()

    # read the names of all the tables
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn).name.tolist()
    tdf = {}

    # read the data from the tables
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    # 找出示例时间（这里用flights表中的actual_departure的最大值）
    example_time = pd.to_datetime(tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    # refresh book_date in the table of bookings
    tdf["bookings"]["book_date"] = (
            pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True) + time_diff
    )

    # The columns with dates that need to be updated
    datetime_columns = ["scheduled_departure", "scheduled_arrival", "actual_departure", "actual_arrival"]
    for column in datetime_columns:
        tdf["flights"][column] = (
                pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    # write the updated dates back to the database
    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        del df  # clear ram
    del tdf  # clear ram

    conn.commit()
    conn.close()

    return local_file


if __name__ == '__main__':

    # execute the date update
    db = update_dates()