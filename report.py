from utils.dbconnect import Sqlite_db

mydb = Sqlite_db()
#print all reports
print("50 most counted words:")
print(mydb.get_most_counted_word())
print("Longest page:")
print(mydb.get_longest_page())
print("Number of unique pages:")
print(mydb.get_unique_pages())
print("Subdomains:")
print(mydb.get_subdomains())