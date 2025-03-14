var express = require("express");
var router = express.Router();
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const User = require("../models/User");

// GET /users/register -> Show Register Page
router.get("/register", function (req, res) {
  res.render("register", { user: req.user || null });
});

// POST /users/register -> Handle User Registration
router.post("/register", async (req, res) => {
  const { name, email, password } = req.body;

  try {
      let user = await User.findOne({ email });
      if (user) {
          return res.render("register", { error_msg: "Email already registered" });
      }

      // Hash the password before saving
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(password, salt);
      console.log("Registering User with Hashed Password:", hashedPassword); // Add logging

      user = new User({ name, email, password: hashedPassword });
      await user.save();

      res.render("login", { success_msg: "You are now registered. Please log in." });
  } catch (err) {
      console.error(err);
      res.render("register", { error_msg: "Something went wrong. Please try again." });
  }
});

// GET /users/login -> Show Login Page
router.get("/login", function (req, res) {
  res.render("login", { user: req.user || null, error_msg: null, success_msg: null });
});

// POST /users/login -> Handle Login
router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
      const user = await User.findOne({ email });
      if (!user || !await bcrypt.compare(password, user.password)) {
          return res.render("login", { error_msg: "Incorrect email or password", success_msg: null });
      }

      const token = jwt.sign({ id: user._id, name: user.name }, process.env.JWT_SECRET, { expiresIn: '1h' });
      res.cookie('token', token, { httpOnly: true });
      res.redirect("/users/dashboard");
  } catch (err) {
      console.error(err);
      res.render("login", { error_msg: "Something went wrong. Please try again.", success_msg: null });
  }
});

// GET /users/profile -> User Profile (Protected)
router.get("/profile", isAuthenticated, function (req, res) {
  res.render("profile", { user: req.user });
});

// GET /users/logout -> Logout
router.get("/logout", function (req, res) {
  res.clearCookie('token');
  res.redirect("/");
});

// Middleware to Protect Routes
function isAuthenticated(req, res, next) {
  const token = req.cookies.token;
  if (!token) {
    return res.redirect("/users/login");
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.redirect("/users/login");
    }
    req.user = decoded;
    next();
  });
}

router.get("/dashboard", isAuthenticated, (req, res) => {
  res.render("dashboard", { user: req.user, success_msg: null, error_msg: null }); // Ensure "views/dashboard.ejs" exists
});

module.exports = router;
