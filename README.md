# EPL Data Collection Project

## Overview

This project serves as a showcase of my proficiency in utilizing SQL and Python, demonstrated through the collection of data from the English Premier League (EPL) using the official API provided by [Premier League](https://www.premierleague.com/). The database consists of 7 tables, and an Entity-Relationship Diagram (ERD) has been prepared to illustrate the relationships between them.

## Features

- **Data Collection:** Utilized Python to interact with the EPL API and gather relevant football data.
- **SQL Database:** Designed and implemented a SQL database with 7 tables to store the collected data.

## Entity-Relationship Diagram (ERD)
![EPL_DatabaseERD.png](/EPL_DatabaseERD.png)

## Data Collection Challenges

During the data collection process from the API, several challenges arose, and here is how I addressed them:

### Problem 1: Data Mismatch Despite Coming from the Same API

**Problem:** Discrepancies were observed in key identifiers such as stadium IDs. Despite referencing the same stadium (e.g., Loftus Road), different IDs were showed in the matches and stadiums endpoints. This discrepancy posed challenges in establishing direct foreign key relationships.

**Solution:** I combined information from both the stadiums and matches APIs using the stadium names and standardized the use of the same ID for a stadium. After that, I temporarily removed constraints between tables using the `NO CHECK CONSTRAINT` command to facilitate smooth data insertion.

### Problem 2: Data Filtering Challenge for Clubs data collection

**Problem:** The [API](footballapi.pulselive.com) used contains information about teams from various leagues. Since the project's goal is limited to the Premier League, I needed a filtering mechanism to only retrieve teams that participated in this league instead of using an infinite loop with increasing team IDs.

**Solution:** I collected data about matches first, then used SQL statements to filter out the unique IDs of teams that participated in the EPL. I proceeded to collect data based on the obtained list of IDs from the SQL statement. After that, I temporarily removed constraints between tables using the `NO CHECK CONSTRAINT` command to facilitate smooth data insertion.

**Note:** Although the solutions to both of my challenges involve using `NO CHECK CONSTRAINT`, and typically, this may introduce some issues for data integrity. However, I can affirm that this is an optimal approach without compromising data integrity.

## Maintenance

To ensure that your data is up to date, each Python file in this project has integrated maintenance and update mechanisms. These mechanisms are designed to keep the data current up to the point in time when each file is executed. Below is an overview of how maintenance and data updating are handled:

### Data Update Process

For each Python file responsible for data collection, the following steps are taken to maintain and update the data:

1. **Check for Existing Data:** The code checks the existing data in the database tables based on primary keys.

2. **Retrieve New Data:** The code interacts with the Premier League API to fetch new data beyond the last update timestamp.

3. **Update Database:** The new data is processed and updated into the respective tables in the SQL database.

### Running the Maintenance Process

To perform data maintenance and update, you can execute the Python files associated with each data collection task. Each file is designed to handle the maintenance and update process independently and keep the data up to date.

**Note:** Make sure that the tables are created and that you have the necessary permissions and connectivity to the SQL database before running the maintenance process.

## Installation

To run this project, you will need to install the following Python libraries. You can install them using the following commands:

```bash
pip install requests
pip install pyodbc
pip install beautifulsoup4
pip install pandas
```

Feel free to run the provided commands to install the required libraries before executing the project.
