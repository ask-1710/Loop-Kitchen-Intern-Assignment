# Loop-Kitchen-Intern-Assignment

Welcome to the Loop-Kitchen-Intern-Assignment repository! This project showcases a backend API developed using the Flask framework in Python, coupled with SQLlite3 for database management. 

The application reads data from sqllite3 DB and generates a month-wise, week-wise, day-wise and hour-wise report for all the restaurants. The report generation is asynchronous and a client can request for multiple reports to be generated at once. 

## Features and Implementation

- **Backend API:** Built using Flask, the backend API facilitates data management and report generation.
- **Database Management:** Utilized SQLlite3 to create and manage static data in the database.
- **Dynamic HTML:** Employed Jinja templates for generating dynamic HTML pages.
- **Modular System:** Implemented a modular architecture using classes, modules, and type hints for a structured codebase.
- **Multithreading:** Developed a trigger+polling architecture using threads, enabling parallelism for micro tasks.
- **Synchronization:** Employed locks for database operations and global variables to prevent race conditions.
- **Parallel Request Handling:** The application efficiently handles multiple client requests for report generation.
- **Data Interpolation:** Implemented a ratio-based interpolation strategy to derive results from available data.
- **Report Delivery:** Converted cumulative reports into dataframes and delivered them as downloadable CSV files.
