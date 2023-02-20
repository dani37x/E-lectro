## About The Project
<a name="readme-top"></a>

E-lectro is a web application in Flask. Its destination is an online shop but centers on non-visual things. This project focuses on security and curious solutions. Full backend project, and what is more, everything terrific works deeply. The project contains ready solutions like Limiter or SQLAlchemy ORM, but there occur own functions with prevalence.

<br>
<div align="center">

  [Roadmap](#roadmap) •
  [Technology stack](#technology_stack) •
  [Installation](#installation) •
  [Contact](#contact)
  
 </div>

## Roadmap

<a name="roadmap"></a>


 

### Built With
<a name="technology_stack"></a>
* FLASK
* SQLALCHEMY
* LIMITER
* FLASK-MAIL
* FLASK-LOGIN
- [x] Protections wrappers:
  - [x] for admin views, check whether a user is an admin
  - [x] for common users, check their ip and account details
- [x] Own Admin management panel with basic operations on a row like
  - [x] edit row
  - [x] delete row
  - [x] add a new row
  - [x] search rows that contain query
- [x] Group actions in the admin panel (many rows):
  - [x] accounts users' activation
  - [x] accounts users' deactivation
  - [x] delete rows
  - [x] delete inactive accounts
  - [x] send test e-mails
  - [x] block accounts
  - [x] backups
  - [x] restore databases
- [x] entries limiter 
- [x] Flask Login
  - [x] Login
  - [x] Authantacion
  - [x] Register
  - [x] Logout
- [x] Effective own validators
  - [x] correct password with website standards
  - [x] Exists user
  - [x] Exists e-mail
- [x] automatic function which takes off a block from users' accounts after a specific date.
- [x] Error handlers
- [x] Event system, which gathers errors, actions to `events.json` which will be performed by users
- [x] Searching input for users which looking for products
- [x] Trending rank. Rank searches from users. Function gathers users queries and creates rank with them, then they are going to appeal on searching input area
- [x] E-mails:
  - [x] no-reply mail
  - [x] reset password mail
  - [x] register code mail
  - [ ] newsletter mail with a recommendation
- [x] user account activation session:
  - [x] mail with the key
  - [x] sets active action
- [x] reset password sessions  
  - [x] limited duration to 15 minutes
  - [x] auto-delete sessions after time
  - [x] hash sessions
  - [x] unique key and session generator
- [x] register session
  -[x] e-mail with key for confirmation
  -[x] account creates after the correct key
  -[x] after 15 minutes session with registration is deleted and an account doesn't create
- [x] password change by a user on account
- [x] function deletes data from json files every specific time   
- [ ] Machine Learning algorithm which will adjust the best products for the shop's customers.
- [ ] shop API
- [ ] multi-device login (max 3)
- [ ] flask bcrypt
- [ ] account lvl
- [ ] payments
- [ ] products list
- [ ] own hash password algorithm
- [ ] own authentication system
- [ ] Database change - from sqlalchemy to SQLITE3
- [ ] newsletters defined for every user

### Installation
<a name="installation"></a>

1. Get a free Mail API Key at [https://mailtrap.io/](https://mailtrap.io/)

2. Clone the repository
   ```sh
   git clone https://github.com/dani37x/E-lectro.git
   ```
3. Install python packages from [requirements.txt](https://github.com/dani37x/E-lectro/blob/master/requirements.txt) in `env`
   ```sh
   pip install ...
   ```
4. Enter your API in `env.py` variables
   ```python
   os.environ['API_KEY'] = 'ENTER YOUR API KEY';
   ```



## Contact
<a name="contact"></a>
📫&nbsp;  **dksluzbowe9@gmail.com**



<p align="left"><a href="#readme-top">back to top</a></p>