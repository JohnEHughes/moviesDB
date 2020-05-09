<h2>Movie DB Demo Program</h2>

Welcome to my evolving practice/demo app!

This program had not been planned beforehand so the code is a bit all over the place!

It started as a simple movie lookup via an API then kept growing as I thought about additional functionality I wanted to practice.

At the moment you can create a user account whose details (username/password/db file name) are stored in an external csv file named userlist.csv.
The user can create or delete accounts which will remove that record from the file.
The user has to establish a validated password and has three attempts to get it right before starting again.
Once 'in', the user has access to their SQLite db. If they have not added any movies to it yet, then the file will not have been created.
If they have or had done previously, then they will have a file. They have the ability to delete this file aswell when they delete their account.

The user can then look up a movie which searched via an API and returns the first ten matches in a summary list. Then a dynamic list is produced for the user to read through then select any of the movies to see more details.
This enhanced detail takes the previous search which found the unique imdbID, and uses that to search again and retrieve the info.
The user can then decide whether to ignore or add the movie to their db.
They can then list movies in the db, view them or delete them. 
I have added a stats option which captures the movie scores from Metascore and IMDB and returns some basic computed info such as highest score/move, lowest scored movie and the average score.



This is a work in progress and I will continue to tinker with it as I think of other ways I can add to it, or make the code better. Perhaps structure it in a more coherent manner.

The next big step will be learning Django to integrate it into a webapp so it has a front end.
 
