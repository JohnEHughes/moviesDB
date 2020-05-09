import matplotlib.pyplot as plt
import pandas as pd


def rating_lists(rows):
    # Statistics using the scores from the movie in the database.
    if len(rows) == 0:
        print('No movies in the database to review.')
        userlist.display_db_movie_list()
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
        for row in rows:
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

        full_data = {'Movie': movies,
                     'Director': directors,
                     'Genre': genres,
                     'Show_Type': show_type,
                     'Country': countries,
                     'IMDB': imdb,
                     'Metascore': metascore
                     }
        dfull = pd.DataFrame(full_data)
        print('==================================================')
        print()
        print(dfull)
        print()
        print('==================================================')

        # Use list comp to create a new IMDB list with el multiplied by 10
        imdb_score_st = [score * 10 for score in imdb]

        # Create a pandas dataframe for practice
        data = {'Movie': movies, 'IMDB': imdb_score_st, 'Metascore': metascore}
        df = pd.DataFrame(data)

        # Create new series of the differences between the review score cols
        difference = abs(df['IMDB'] - df['Metascore'])

        # Create bools to determine which column has the most higher scores
        dif_i = df[df['IMDB'] < df['Metascore']]
        dif_m = df[df['IMDB'] > df['Metascore']]

        # Count the shows by country and save the number and country. Split the col item if needed
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

        for k, v in country_count.items():
            country_most_name.append(k)
            country_most_amount.append(v)

        country_most_name_max = max(country_most_amount)
        country_most_name = country_most_name[country_most_amount.index(country_most_name_max)]

        # Display the above findings to the user in a verbose way
        print()
        print('         IMDB Movie Review Scores')
        print(f'There are {len_imdb} scores with an average of {sum_imdb /len_imdb}')
        print(f'Highest scoring show is {max_imdb_movie} with a score of {max_imdb}')
        print(f'lowest scoring show is {min_imdb_movie} with a score of {min_imdb}')
        print()
        print('      Metascores Movie Review Scores')
        print(f'There are {len_metascore} scores with an average of {sum_metascore/len_metascore}')
        print(f'Highest scoring show is {max_metascore_movie} with a score of {max_metascore}')
        print(f'Lowest scoring show is {min_metascore_movie} with a score of {min_metascore}')
        print()
        print('==================================================')
        print()
        print('As the two Websites score the shows with different scales, to compare them, I have multiplied the '
              'IMDB scores by 10.')
        print()
        print(df)
        print()
        print('==================================================')
        print()
        print('Now with standardised scores, I can now compare both score lists:')
        print()
        print(f'The average difference between the sites for all the shows is {difference.mean():.2f}')
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
        print()
        print('==================================================')
        print()
        print(f"{country_most_name} has produced the most shows in your collection with {country_most_name_max}")
        print()
        print('==================================================')
        print()
        director_count = dfull['Director'].value_counts()

        # Count the shows by director and save the number and director
        # Count the total number of unique directors
        if director_count.count() == 1:
            one_director = dfull['Director'].value_counts()[:].index.tolist()[0]
            one_director_amount = dfull['Director'].value_counts()[0]
            if one_director_amount == 1:
                print(f'{one_director} is your most popular director with {one_director_amount} show')
            else:
                print(f'{one_director} is your most popular director with {one_director_amount} shows')

        elif director_count[0] > director_count[1]:
            one_director = dfull['Director'].value_counts()[:].index.tolist()[0]
            one_director_amount = dfull['Director'].value_counts()[0]
            if one_director_amount == 1:
                print(f'{one_director} is your most popular director with {one_director_amount} show')
            else:
                print(f'{one_director} is your most popular director with {one_director_amount} shows')

        elif director_count[0] == director_count[1]:
            two_director = dfull['Director'].value_counts()[:1].index.tolist()[0]
            two_director_amount = dfull['Director'].value_counts()[:1][0]
            if two_director_amount == 1:
                print(f'{two_director} is your most popular director with {two_director_amount} show')
            else:
                print(f'{two_director} is your most popular director with {two_director_amount} shows')

        # Create a simple plot to show the scores against movie titles
        plt.plot(movies, imdb_score_st, c='r', label='IMDB')
        plt.plot(movies, metascore, c='b', label='Metascore')
        plt.xticks(rotation=90)
        plt.xlabel('Movies')
        plt.ylabel('Scores (%)')
        plt.legend()
        plt.title('Comparing IMDB and Metascore review scores for each movie.')
        plt.show()