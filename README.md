# Golden Card
This is a website of souvenir chocolate "Golden Card".

# Functionality
- view information on the site pages;
- view and leave reviews;
- register and log in on the site;
- add photos to the user's personal profile.

### flsite.py: 
This is the main file that runs the site:
- enter the path to this file in the command line (**cd \path_to_file**);
- launch the file (**python flsite.py**);
- follow the link generated by the command line.

### Directory "static" 
- It contains a subdirectory **"css"**, containing styles for all pages of the site.
- The subdirectories **"images_html"** and **"video_html"** contain pictures and videos posted on the site, respectively.

### Directory "templates"
It contains the html files of all the pages of the site. 
The rest of the html files are inherited from the base file "base.html".

### site.db
It contains database tables. To generate your database: 
- enter the path to this file in the command line (**cd \path_to_file**);
- go to the python interpreter (enter '**python**');
- enter '**from flsite import create_db**'
- enter '**create_db**'



