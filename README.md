# Movie Voter
#### Video Demo:  <https://www.youtube.com/watch?v=OH_oKTe15-E>
#### Description:
    My CS50 Final project is a web-based application designed to help groups of people decide what movie(s) to watch together.
To complete this project, I utilized Python, Flask, HTML, CSS, Javascript, JINJA and SQL. When the program is first opened
the user is prompted to either login or register to create an account. Once they've done this they can access the website
and create their first group. They can name their group whatever they'd like (as long as they give it a name), they will
then be able to add other users to this group via the 'add members' tab. They can view their groups and the corresponding
members in the 'My Groups' tab. Next a user can search for a desired film in the 'search' tab. If the film is in the database,
it will display the films title and release year. The user can then add the film to one of their groups 'watch_list' using the
'Add to watch list' tab. Finally they can view all the films that have been added to all of their groups in the rankings tab.
Displayed under each group will be a movies title, release year and the number of group members who have submitted the film to
the group watch list. Importantly, films are ranked by the number of people who have submitted them to the group to easily
distinguish which movies are the most popular among the group.
    In the future I would aim to make it easier to vote for movies that have already been submitted to the group via some 'like'
feature rather than having to resubmit the same movie into the group multiple times. Ultimately I was unable to implement this
feature as I struggled with form submission in HTML. However, I am confident with more practice in web design I will be comfortably
able to implement this feature in the future
    My project folder is comprised of a templates folder which contains HTML files corresponding to each page of the site. The
site navigates between these files using app.py, a python file which serves as the brains of the operation. For every HTML page,
a function is defined in app.py which describes which arguments will be passed to the page so that the site can dynamically respond
to user input. There is another python file 'helpers.py' which defines several helper functions used in app.py There is also a static
folder which contains a CSS file to help stylize the site. Finally there is a SQL database, 'project.db' that contains all stored
information regarding users, groups, movies and watch_lists. To store movie information, I used the movies.db database that was used
in an earlier CS50 problem set. At present my site only takes advantage of the movies title, id and release year but because I have
access to the entire database I could forseeably add information about a movies ratings, cast and crew or allow users to search for
movies by lead actor/actress or director.