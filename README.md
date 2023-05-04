## E-lectro
<a name="readme-top"></a>

E-lectro is a web application built using the Flask framework, with the main purpose of serving as an online shop. However, unlike traditional e-commerce websites, E-lectro focuses on non-visual aspects, such as security and unique solutions for specific problems.

One such solution is the Random Forest Classifier, which is used to classify users and recommend suitable products for them. This algorithm takes into account various factors such as past purchases, search history, and other user data to make personalized product recommendations.

Another feature of E-lectro is the use of Redis queue, which is used as an asynchronous task queue. This allows for faster processing of user requests and helps to improve the overall performance of the application.
The project is a full backend solution, with a strong emphasis on security. It includes ready-made solutions like entries limiter and SQLAlchemy ORM, but also incorporates custom functions to solve specific problems.

Overall, E-lectro is a well-designed and fully-functional web application that demonstrates the power and flexibility of the Flask framework. Its unique features and emphasis on security make it a standout project in the world of e-commerce.

<br>
<div align="center">

  [Roadmap](#roadmap) •
  [Technology stack](#technology_stack) •
  [Installation](#installation) •
  [Contact](#contact)
  
 </div>

## Roadmap

<a name="roadmap"></a>

- [x] Own Admin management panel with basic operations on a row like
  - [x] edit row
  - [x] delete row
  - [x] add a new row
  - [x] search rows that contain query
  - [x] sort system descending and ascending by database tables and their column properties
- [x] Protections wrappers:
  - [x] wrapper for admin views, check whether a user is an admin
  - [x] wrapper for common users, check their ip and account details
  - [x] wrapper that co-works with my captcha system against bots
- [x] Group actions in the admin panel (many rows):
  - [x] accounts users' activation
  - [x] accounts users' deactivation
  - [x] delete rows
  - [x] delete inactive accounts
  - [x] send test e-mails
  - [x] block accounts
  - [x] backups
  - [x] restore databases
  - [x] newsletter for registered users
  - [x] set timed price hikes for products
  - [x] set timed discounts for products
  - [x] set the previous price for every product
  - [x] set the lowest price for products from last month
  - [x] set the highest price for products from last month
  - [x] set the random price for products from last month
- [x] Redis and Redis queue
  - [x] Redis queue and workers
  - [x] old functions with async queue usage
  - [x] time to cancel task from queue
  - [x] delete cancelled task from rq history
- [x] Forms
  - [x] Register form
  - [x] Login form 
  - [x] Key form
  - [x] New Password form
  - [x] Remind Password form
- [x] Flask Login
  - [x] Login
  - [x] Authantacion
  - [x] Register
  - [x] Logout
- [x] Effective own validators
  - [x] correct password with website standards
  - [x] Exists user
  - [x] Exists e-mail
  - [x] not null validator for HTML form.
- [x] automatic function which takes off a block from users' accounts after a specific date.
- [x] Error handlers
- [x] entries limiter
- [x] Event system, which gathers errors, actions to `EVENTS.json` which will be performed by users
- [x] Searching input for users which looking for products
- [x] Trending rank. Rank searches from users. Function gathers users queries and creates rank with them, then they are going to appeal on searching input area. Disallowed words do not contribute to the total
- [x] E-mails:
  - [x] no-reply mail
  - [x] reset password mail
  - [x] register code mail
  - [x] newsletter mail with the latest products
- [x] user account activation session:
  - [x] mail with the key
  - [x] sets active action
- [x] reset password sessions  
  - [x] limited duration to 15 minutes
  - [x] auto-delete sessions after time
  - [x] hash sessions
  - [x] unique key and session generator
- [x] register session
  - [x] e-mail with key for confirmation
  - [x] account creates after the correct key
  - [x] after 15 minutes session with registration is deleted and an account doesn't create
- [x] shop views
  - [x] list of categories
  - [x] dynamic list of products in category
  - [x] dynamic single page for every product
  - [x] sort system descending and ascending by product properties such as name, company, category, price
- [x] password change by a user on account
- [x] cookies with category of product with price from the searched product by the user
- [x] APScheduler
  - [x] deletes expired data from json files every specific time
- [x] Newsletter
  - [x] an e-mail for registered users with five of the latest products with links
  - [x] register for the newsletter
  - [x] unregister for  the newsletter
- [x] ML algorithm - *RandomForestClassifier*
  - [x] Machine Learning algorithm which adjust the best products for the shop's customers in every category of products
  - [x] upgrade ML algorithm with many indicators
- [x] shop API
- [x] flask bcrypt
- [x] User personal data
  - [x] editable
  - [x] when the user wants to change 'the username' the app checks whether the new name is free
  - [x] when the user wants to change the e-mail app sends an e-mail message with a code. After 15 minutes code will expire Without code, change is not possible
- [x] Own captcha system. Every user has only three chances before logout
  - [x] random quizzes with random letters and sizes
  - [x] the captcha wrapper for views.
  - [x] registration how many times the user did not pass the captcha. Consequences with it(block of account)
  - [x] only three tries for every user and only three times the user can't pass the captcha test by seven days
  - [ ] after a correct answer earlier wrong answers are deleted from the register
- [x] Price system
  - [x] the recording system in PRICES.json tracks every action taken within the price system.
  - [x] timed promotions for products
  - [x] timed price hike for products
  - [x] a super user can easily change the previous price of a product
  - [x] the lowest price function informs the user about the lowest price observed in the last 30 days
  - [x] If a product is on promotion, the highest price function informs the user about the highest price recorded within the last 30 days.
  - [x] users can see how much money they will save on each product during the promotion, thanks to the discount
- [x] User panel
  - [x] a user can change his nickname, e-mail, and the personal data
- [ ] better Readme section of installation which depict the correct process with Redis and Redis queue
- [ ] multi-device login (max 3)
- [ ] account lvl and points system with discounts.
- [ ] payments for products
- [ ] boughted products by users
- [ ] list of products
- [ ] own hash password algorithm
- [ ] own authentication system


### Built With
<a name="technology_stack"></a>
* FLASK
* SKLEARN
* SQLALCHEMY
* REDIS
* REDIS QUEUE
* APSCHEDULER
* LIMITER
* FLASK-MAIL
* FLASK-LOGIN
* FLASK BCRYPT


### Installation
<a name="installation"></a>


1. Clone the repository
   ```sh
   git clone https://github.com/dani37x/E-lectro.git
   ```
2. Install python packages from [requirements.txt](https://github.com/dani37x/E-lectro/blob/master/requirements.txt) in `env`
   ```sh
   pip install -r requirements.txt
   ```
3. Get a free Mail API Key at [https://mailtrap.io/](https://mailtrap.io/)
4. Enter your API keys in variables in secret file
   ```python
   os.environ['MAIL_USERNAME'] = '';
   os.environ['MAIL_PASSWORD'] = '';
   ```
5. If you are Linux user go to step *11*.
6. Open Powershell as Administrator
7. Run command
```sh
wsl --install
```
8. After correct installation open WSL on Windows
9. Activate virtual environment
10. Install Python and Python's packages from `requirements.txt` in environment.
11. Run redis-server with command
```sh
sudo service redis-server start
```
12. Run Redis worker with command
  ```
  rq worker
  ```


## Contact
<a name="contact"></a>
📫&nbsp;  **dksluzbowe9@gmail.com**



<p align="left"><a href="#readme-top">back to top</a></p>
