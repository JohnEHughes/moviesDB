import sqlite3
import requests
import csv
import os
import re
import os.path
import config
import matplotlib.pyplot as plt
import pandas as pd

class User:

    def __init__(self, name, password, database):
        # The User is constructed with their name, password and database
        self.name = name
        self.password = password
        self.database = database
        self.movie_count = self.movie_count_meth()
        # API URL to retrieve movie data
        self.url = config.api_url
        self.headers = {
            'x-rapidapi-host': config.api_host,
            'x-rapidapi-key': config.api_key
                        }
        self.rows = self.get_db_rows()

    def __str__(self):
        return f"The account of {self.name}"

    def movie_count_meth(self):
        # Method to return number of movies in the database
        con = sqlite3.connect(self.database)
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM MovieInfo')
            rows = cur.fetchall()
            self.movie_count = len(rows)
            return self.movie_count
        except sqlite3.Error:
            print('Database empty!')
        con.close()

    def find_show(self, querystring):
        # Search film API and return json data or -1 if not found
        response = requests.request("GET", self.url, headers=self.headers, params=querystring)
        json_movies = response.json()
        if json_movies['Response'] == 'False':
            return -1
        return json_movies

    def detail_display(self, movie):
        # Uses the IMDB ID found in the previous method, to retreive data from another API link and display details
        querystring = {"i": movie, "r": "json", "plot": "full"}
        response = requests.request("GET", self.url, headers=self.headers, params=querystring)
        json_movie = response.json()
        print()
        print(f"{json_movie['Title']} >> released in {json_movie['Year']} and directed by {json_movie['Director']}.")
        print()
        print(f"It stars {json_movie['Actors']} in this {json_movie['Genre']} {json_movie['Type']}.")
        print()
        print(f"The movie plot: {json_movie['Plot']}")
        print()
        print(f"Runtime: {json_movie['Runtime']} \t\t\t <<  Ratings: Metascore - {json_movie['Metascore']} / IMDB - {json_movie['imdbRating']}  >>")
        print()
        save_user = input("Do you wish to save in database? y/n ")
        if save_user == 'y':
            self.save_in_database(json_movie)

    def display_shows(self, shows):
        # Takes the json data and displays a dynamic list of searched movies.
        # A dynamic menu is then created for the user to choose
        c = 0
        movie_id = []
        movie_name = []
        movie_year = []
        for movie in shows['Search']:
            c += 1
            if c == 11:
                break
            print()
            print(f"{c}). {movie['Title']}, a {movie['Year']} {movie['Type']}")
            if movie['Poster'] != "N/A":
                print(movie['Poster'])
                print()
            movie_id.append(movie['imdbID'])
            movie_name.append(movie['Title'])
            movie_year.append(movie['Year'])

        flag = True
        while flag:
            print()
            s = ""
            for i, v in enumerate(movie_name):
                s += f"\t{i + 1} - {v} ({movie_year[i]})\n"
            s += "\tb - go back\n"
            print("If you want to see more detail on one of these films type:")
            print(s)
            user_detail = input()
            if user_detail == 'b':
                self.user_input()
            elif user_detail.isdigit() and int(user_detail) <= len(movie_id):
                movie_index = int(user_detail)
                self.detail_display(movie_id[movie_index - 1])
            else:
                print('Invalid entry, please try again.')
                self.display_shows(shows)

    def menu(self, qs):
        # Checks if the querystring passed are correct and passes to another method to process if correct
        flag = True
        while flag:
            if qs == -1:
                self.menu()
            else:
                shows = self.find_show(qs)
                if shows == -1:
                    print("Show not found, please try again.")
                    self.user_input()
                else:
                    self.display_shows(shows)

    def user_input(self):
        # One of the main menus once user record established. User now chooses to go back,
        # or to display their movies saved in db, look up a movie's details or quit
        print()
        choice = input("""Please select from the following: 
        s - switch user
        d - display DB movies
        l - to look a movie up
        q - to quit
        """)
        if choice == 'l':
            name = input('Film: ')
            if name == 'q' or name == '':
                self.user_input()
            year = input('If year known or type 0 if not: ')
            if year == '0' or "":
                year = ""
            if name == 'q':
                self.user_input()
            type_show = input('Type of show: movie, series, episode or type 0 if not: ')
            if type_show == '0' or "":
                type_show = ""
            if name == 'q':
                self.user_input()
            querystring = {
                "page": "1",
                "y": year,
                "r": "json",
                "s": name,
                "type": type_show
            }
            self.menu(querystring)
        elif choice == 'd':
            if self.rows == -1:
                print('Empty database - please save a film.')
                self.user_input()
            else:
                self.display_db_movie_list()
        elif choice == 'q':
            exit()
        elif choice == 's':
            user_menu()
        else:
            print('Invalid choice, please enter l, d or q ')
            self.user_input()


# ================== Database =======================================================

    def get_db_rows(self):
        # Class method to return rows from db or -1 if empty
        con = sqlite3.connect('johnmoviesdb.db')
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM MovieInfo')
            rows = cur.fetchall()
            self.rows = rows
        except sqlite3.Error:
            return -1
        con.close()
        return self.rows

    def display_db_movie_list(self):
        # Displays number in list and then an enumerated dynamic list of user's movies
        list_len = len(self.rows)
        if list_len == 0:
            print("Database empty!")
            self.menu()
        else:
            print()
            if list_len == 1:
                print(f"There is {list_len} movie in the database:")
            else:
                print(f"There are {list_len} movies in the database:")
            self.rows.sort()
            for i, row in enumerate(self.rows):
                print(f"{i + 1}). {row[0]}, ({row[1]}) - Director: {row[5]},  Genre: {row[3]}, Runtime: {row[2]}")
        print()
        db_choice = input(
            """Please choose from the following:
            d) Detailed movie view
            e) Erase movie
            s) Score statistics
            b) Back
            """)
        movie_name_list = [row[0] for row in self.rows]

        if db_choice == 'b':
            self.user_input()
        elif db_choice == 'd':
            try:
                movie_index = int(input('Enter number of movie to get more detail: ').strip())
            except ValueError:
                print('Please type a valid number.')
                self.display_db_movie_list()
            if (movie_index - 1) <= len(movie_name_list):
                movie_choice = movie_name_list[movie_index - 1]
                self.display_db_movie_detail(movie_choice)
                self.display_db_movie_list()
            else:
                print('Movie not in database or name incorrect.')
                self.display_db_movie_list()
        elif db_choice == 'e':
            movie_index = int(input('Enter number of show to delete from database: ').strip())
            if (movie_index - 1) <= len(movie_name_list):
                movie_choice = movie_name_list[movie_index - 1]
                self.deleteRecord(movie_choice)
                self.display_db_movie_list()
            else:
                print('Movie not in database or name incorrect.')
                self.display_db_movie_list()
        elif db_choice == 's':
            self.rating_lists()
            self.display_db_movie_list()
        else:
            print('Invalid selection')
            self.display_db_movie_list()

    def display_db_movie_detail(self, name):
        # Displays more details of the user's movies in their db
        for row in self.rows:
            if row[0] == name:
                print(f"""
                {row[0]}, ({row[1]}) 
                Director: {row[5]},
                Genre: {row[3]},
                Runtime: {row[2]},
                Type: {row[4]},
                Plot: {row[6]},
                Country: {row[7]}
                """)

    def rating_lists(self):
        # Statistics using the scores from the movie in the database.
        if len(self.rows) == 0:
            print('No movies in the database to review.')
            self.display_db_movie_list()
        else:
            imdb = []
            metascore = []
            movie_dict = {}
            movies = []
            countries = []
            directors = []
            genres = []
            show_type = []

            # Create dictionary from the user db
            for row in self.rows:
                movie_dict[row[0]] = {
                    'Genre': row[3],
                    'Show Type': row[4],
                    'Director': row[5],
                    'Country': row[7],
                    'imdb': row[9],
                    'metascore': row[8]
                }

            # From dict populate lists for the scores and movie titles. I could have done this in the previous loop
            # but I wanted to practice looping through dicts
            for movie, v in movie_dict.items():
                movies.append(movie)
                imdb.append(v['imdb'])
                metascore.append(v['metascore'])
                countries.append(v['Country'])
                directors.append(v['Director'])
                genres.append(v['Genre'])
                show_type.append(v['Show Type'])

            # Finding highest score for each reviewer and movie title
            max_imdb = max(imdb)
            max_imdb_movie = movies[imdb.index(max_imdb)]
            max_metascore = max(metascore)
            max_metascore_movie = movies[metascore.index(max_metascore)]

            # Finding lowest score for each reviewer and movie title
            min_imdb = min(imdb)
            min_imdb_movie = movies[imdb.index(min_imdb)]
            min_metascore = min(metascore)
            min_metascore_movie = movies[metascore.index(min_metascore)]

            # Calculating variables for use in later averages
            sum_imdb = sum(imdb)
            sum_metascore = sum(metascore)
            len_imdb = len(imdb)
            len_metascore = len(metascore)

            # Use list comp to create a new IMDB list with el multiplied by 10
            imdb_score_st = [score * 10 for score in imdb]

            # Create a simple plot to show the scores against movie titles
            plt.plot(movies, imdb_score_st, c='r', label='IMDB')
            plt.plot(movies, metascore, c='b', label='Metascore')
            plt.xticks(rotation=90)
            plt.xlabel('Movies')
            plt.ylabel('Scores (%)')
            plt.legend()
            plt.title('Comparing IMDB and Metascore review scores for each movie.')
            # plt.show()

            # Create a pandas dataframe for practice
            data = {'Movie': movies, 'IMDB': imdb_score_st, 'Metascore': metascore}
            df = pd.DataFrame(data)

            full_data = {'Movie': movies,
                         'Director': directors,
                         'Genre': genres,
                         'Show_Type': show_type,
                         'Country': countries,
                         'IMDB': imdb_score_st,
                         'Metascore': metascore
                         }
            dfull = pd.DataFrame(full_data)

            print(dfull)

            # Create new series of the differences between the review score cols
            difference = abs(df['IMDB'] - df['Metascore'])

            # Create bools to determine which column has the most higher scores
            dif_i = df[df['IMDB'] < df['Metascore']]
            dif_m = df[df['IMDB'] > df['Metascore']]

            # Count the shows by country and save the number and country
            country_count = {}
            for c in dfull['Country']:
                c_l = c.split(',')
                for i in c_l:
                    i = i.strip()
                    if i in country_count:
                        country_count[i] += 1
                    else:
                        country_count[i] = 1

            # Count the amount of occurences, list and work out max
            country_most_name = []
            country_most_amount = []

            for k,v in country_count.items():
                country_most_name.append(k)
                country_most_amount.append(v)

            country_most_name_max = max(country_most_amount)
            country_most_name = country_most_name[country_most_amount.index(country_most_name_max)]

            # Display the above findings to the user in a verbose way
            print()
            print('         IMDB Movie Review Scores')
            print(f'There are {len_imdb} scores with an average of {sum_imdb/len_imdb}')
            print(f'Highest scoring show is {max_imdb_movie} with a score of {max_imdb}')
            print(f'lowest scoring show is {min_imdb_movie} with a score of {min_imdb}')
            print()
            print('      Metascores Movie Review Scores')
            print(f'There are {len_metascore} scores with an average of {sum_metascore/len_metascore}')
            print(f'Highest scoring show is {max_metascore_movie} with a score of {max_metascore}')
            print(f'Lowest scoring show is {min_metascore_movie} with a score of {min_metascore}')
            print('==================================================')

            print()
            print('As the two Websites score the shows with different scales, to compare them, I have multiplied the '
                  'IMDB scores by 10.')
            print()
            print(df)
            print('==================================================')

            print()
            print('Now with standardised scores, I can now compare both score lists:')
            print()
            print(f'The average difference between the sites for all the shows is {difference.mean()}')
            print()

            # Conditionals to determine the higher reviewer count
            if len(dif_i) < len(dif_m):
                reviewer_high = 'Metascore'
                mlen = len(dif_m)
            elif len(dif_i) == len(dif_m):
                reviewer_high = 'o'
            else:
                reviewer_high = 'IMDB'
                mlen = len(dif_i)

            if reviewer_high == 'o':
                print('Both Review Sites have an equal amount of higher rated shows than the other.')
            else:
                print(f'{reviewer_high} have given higher scores to more shows - {mlen}/{len_imdb}.')

            print('==================================================')

            print(f"{country_most_name} has produced the most shows in your collection with {country_most_name_max}")
            print()

            director_count = dfull['Director'].value_counts()

            print('==================================================')

            # Count the shows by director and save the number and director
            # Count the total number of unique directors
            if director_count[0] > director_count[1]:
                one_director = dfull['Director'].value_counts()[:].index.tolist()[0]
                one_director_amount = dfull['Director'].value_counts()[0]
                if one_director_amount == 1:
                    print(f'{one_director} is your most popular director with {one_director_amount} show')
                else:
                    print(f'{one_director} is your most popular director with {one_director_amount} shows')

            if director_count[0] == director_count[1]:
                two_director = dfull['Director'].value_counts()[:1].index.tolist()[0]
                two_director_amount = dfull['Director'].value_counts()[:1][0]
                if two_director_amount == 1:
                    print(f'{two_director} is your most popular director with {two_director_amount} show')
                else:
                    print(f'{two_director} is your most popular director with {two_director_amount} shows')
            self.display_db_movie_list()

    def save_in_database(self, json_data):
        # Once film is looked up in detail, option to save that film in the user db.
        title = json_data['Title'].title()
        # Goes through the json dataset and extracts information if it is available
        if json_data['Year'] != 'N/A':
            year = int(json_data['Year'])
        if json_data['Runtime'] != 'N/A':
            runtime = json_data['Runtime'].split()[0] + 'mins'
        if json_data['Genre'] != 'N/A':
            genre = json_data['Genre']
        if json_data['Type'] != 'N/A':
            show_type = json_data['Type']
        if json_data['Director'] != 'N/A':
            director = json_data['Director']
        if json_data['Plot'] != 'N/A':
            plot = json_data['Plot']
        if json_data['Country'] != 'N/A':
            country = json_data['Country']
        if json_data['Metascore'] != 'N/A':
            metascore = float(json_data['Metascore'])
        else:
            metascore = -1
        if json_data['imdbRating'] != 'N/A':
            imdb_rating = float(json_data['imdbRating'])
        else:
            imdb_rating = -1
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        # SQL commands
        cur.execute('''CREATE TABLE IF NOT EXISTS MovieInfo 
        (Title TEXT, Year INTEGER, Runtime TEXT, Genre TEXT, Show_Type TEXT, Director TEXT, Plot TEXT,Country TEXT, Metascore REAL, IMDBRating REAL)''')

        cur.execute('SELECT Title FROM MovieInfo WHERE Title = ? ', (title,))
        row = cur.fetchone()

        if row is None:
            cur.execute('''INSERT INTO MovieInfo (Title, Year, Runtime, Genre, Show_Type, Director, Plot, Country, Metascore, IMDBRating)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                        (title, year, runtime, genre, show_type, director, plot, country, metascore, imdb_rating))
            print("Save successful!")
            # Commits the change and close the connection to the database
            conn.commit()
            conn.close()
            self.get_db_rows()
            self.user_input()
        else:
            print("Show already found. No update made.")

    def deleteRecord(self, movie):
        # Deletes the movie from the user's db
        try:
            conn = sqlite3.connect(self.database)
            cur = conn.cursor()
            # Deleting single record now
            sql_delete_query = "DELETE from MovieInfo where Title = '%s';" % movie
            cur.execute(sql_delete_query)
            conn.commit()
            cur.close()
            self.get_db_rows()
            print()
            print("Movie deleted successfully ")
        except sqlite3.Error as error:
            print("Failed to delete movie from database", error)

    # ========================CSV========================================================


def create_user(name):
    # Creates and saves individual user details into an external CSV file
    print()
    create_choice = input('Do you want to create a record? y/n: ').strip().lower()
    if create_choice == 'y':

        while True:
            print(
    """A strong password is needed, please ensure the below:
    - Minimum 6 characters.
    - The alphabets must be between [a-z]
    - At least one alphabet should be of Upper Case [A-Z]
    - At least 1 number or digit between [0-9].
    - At least 1 character from [ _ or @ or $ or ? or ! or & or *].
    """)
            create_pw = input('Please enter a password: ').strip()
            if password_validator(create_pw):
                break

        user_db = name + 'moviesdb.db'
        user_record = [name, create_pw, user_db]
        try:
            record_user(user_record, 'userlist.csv')
            print(f"{name.title()}'s details recorded successfullY!")
            print()
            user_menu()
        except ValueError:
            print('Writing failed, please try again.')
            create_user(name)
    elif create_choice == 'n':
        user_menu()
    else:
        print('Invalid choice.')
        create_user(name)


def password_validator(pw):
    flag = 0
    while True:
        if len(pw) < 6:
            flag = -1
            break
        elif not re.search("[a-z]", pw):
            flag = -1
            break
        elif not re.search("[A-Z]", pw):
            flag = -1
            break
        elif not re.search("[0-9]", pw):
            flag = -1
            break
        elif not re.search("[_@$?£!&*]", pw):
            flag = -1
            break
        else:
            flag = 0
            print("Valid Password")
            return True

    if flag == -1:
        print("Not a Valid Password")


def record_user(data, path):
    # Sub method used in create_user method
    with open(path, "a+", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def delete_user_details(user_name, path='userlist.csv'):
    # Delete user record detail in the CSV file
    col_data = ['username', 'password', 'database']
    lines = list()
    with open(path, 'r') as fr:
        reader = csv.reader(fr)
        for row in reader:
            lines.append(row)
            for i in row:
                if i == user_name:
                    lines.remove(row)
    with open(path, 'w', newline='') as fw:
        writer = csv.writer(fw)
        writer.writerows([col_data])
        writer.writerows(lines[1:])
    print('Record deleted.')
    db_file = user_name + 'moviesdb.db'
    if os.path.exists(db_file):
        os.remove(db_file)
        print('DB file deleted.')


def user_menu():
    # Main menu for the application
    user_main = input(
    """Welcome, please select from the following:
    a) Add/Select User
    l) List Users
    q) Quit 
    """)
    if user_main == 'l':
        list_users()
        user_menu()
    elif user_main == 'a':
        user_name = input("Please enter user name: ").lower().strip()
        print()
        print(f'Hello, {user_name.title()}!')
        if check_user(user_name):
            pw_attempts = 1
            password, db = password_checker(user_name)
            while pw_attempts < 4:
                if pw_attempts == 1:
                    pw_s = "Please enter your password (Max 3 attempts): "
                else:
                    pw_s = f'Please try again ({pw_attempts}/3): '

                user_pw = input(pw_s).strip()
                pw_attempts += 1
                if user_pw == password:
                    break
                else:
                    continue
            else:
                print('You have failed three times, please start again.')
                user_menu()
            print('Password correct! - please select from the following:')
            flag = True
            while flag:
                user_db_choice = input(
        """
        b) Back
        c) Continue
        d) Delete User
        """).lower().strip()
                if user_db_choice == 'd':
                    delete_user_details(user_name)
                    user_menu()
                elif user_db_choice == 'c':
                    self = User(user_name, password, db)
                    self.user_input()
                    flag = False
                elif user_db_choice == 'b':
                    user_menu()
                else:
                    print('Invalid entry')
        else:
            print('Looks like no records exist for you!')
            create_user(user_name)
    elif user_main == 'q':
        print('Goodbye!')
        exit()
    else:
        print('Invalid input')
        user_menu()


def password_checker(name):
    # Retrieves password and db names from CSV file
    with open('userlist.csv', 'r') as f:
        rows = csv.reader(f)
        for row in rows:
            if row[0] == name:
                password = row[1]
                db = row[2]
                return password, db


def list_users():
    # Displays names of users stored in CSV file
    with open('userlist.csv', 'r') as f:
        rows = csv.reader(f)
        rows = list(rows)[1:]
        if not rows:
            print("There are no records available.")
        else:
            print('User List')
            print('---------')
            for row in rows:
                print(row[0].title())
            print()


def check_user(name):
    # Checks if user name is in the CSV file.
    with open('userlist.csv', 'r') as f:
        rows = csv.reader(f)
        for row in rows:
            if not row == []:
                if row[0] == name:
                    print('Record exists')
                    return True
        return False


user_menu()
# rating_lists()