## About The Project
<a name="readme-top"></a>

E-lectro is a web application in Flask. Its destination is online shop, but  center on non-visual things. This project focuses on security and curious  solutions. Full backend project, what is more, everything terrific works deeply. Project contains ready solutions like Limiter or SQLAlchemy ORM, but definitely there occur own functions with prevalence.



## Roadmap
- [x] Protections wrappers:
  - [x] for admin views, check wheter user is admin
  - [x] for common users, check their ip and account details
- [x] Own Admin managment panel with basic operations on row like
  - [x] edit row
  - [x] delete row
  - [x] add new row
  - [x] search rows which contain query
- [x] Group actions in admin panel (many rows):
  - [x] accounts users's activation
  - [x] accounts users's deactivation
  - [x] delete rows
  - [x] send test e-mails
  - [x] block accounts
  - [x] backups
  - [ ] restore databases
- [x] Flask Login
  - [x] Login
  - [x] Authantacion
  - [x] Register
  - [x] Logout
- [x] Effective own validators
  - [x] correct password with website standards
  - [x] Exists user
  - [x] Exists e-mail
- [x] automatic function which take off block from users's accounts after specific date.
- [x] Error handlers
- [x] Event system, which gather errors, actions to `events.json` which will be perform
- [x] Searching input for users which looking for products
- [x] Trending rank. Rank searches from users. Function gather users queries and create rank with them, then they are going to appeal on searching input area
- [x] E-mails:
  - [x] no-reply mail
  - [ ] reset password  
  - [ ] register mail
- [ ] reset password sessions  
  - [ ] limited duration to 15 minutes
  - [ ] auto-delete sessions after time
  - [ ] hash sessions
  - [ ] key and session generator
- [ ] Machine Learning algorithm which will adjust the best products for shop's customers.
- [ ] password change by user on account
- [ ] shop API
- [ ] multi account login (max 3)

 

### Built With
* FLASK
* SQLALCHEMY
* LIMITER
* FLASK-MAIL
* FLASK-LOGIN


### Installation

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
📫&nbsp;  **dksluzbowe9@gmail.com**



<p align="left"><a href="#readme-top">back to top</a></p>
