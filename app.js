var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var session = require('express-session');
var passport = require('./config/passport'); // Import Passport.js
require('dotenv').config(); // Load environment variables

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var authRouter = require('./routes/auth'); // Add authentication routes

var app = express();

// MongoDB Connection
var connectDB = require('./config/db');
connectDB(); // Connect to MongoDB

// View engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Express Session
app.use(
  session({
    secret: process.env.SESSION_SECRET, // Store secret in .env
    resave: false,
    saveUninitialized: false,
  })
);

// Initialize Passport.js
app.use(passport.initialize());
app.use(passport.session());

// Routes
app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/auth', authRouter); // Authentication routes

// Catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

// Error handler
app.use(function (err, req, res, next) {
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
