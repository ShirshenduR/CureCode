var express = require("express");
var router = express.Router();
var passport = require("passport");
var User = require("../models/User");
var bcrypt = require("bcryptjs");

// GET /users/register -> Show Register Page
router.get("/register", function (req, res) {
  res.render("register", { user: req.user || null });
});

// POST /users/register -> Handle User Registration
router.post("/register", async function (req, res) {
    const { name, email, password } = req.body;
  
    try {
      if (!name || !email || !password) {
        return res.status(400).send("All fields are required!");
      }
  
      let user = await User.findOne({ email });
      if (user) {
        return res.status(400).send("User already exists. Try logging in.");
      }
  
      const hashedPassword = await bcrypt.hash(password, 10);
      user = new User({ name, email, password: hashedPassword });
      await user.save();
  
      console.log("User Registered:", user);
      res.redirect("/users/login");
    } catch (error) {
      console.error("Registration Error:", error);
      res.status(500).send("Internal Server Error");
    }
  });
  

// GET /users/login -> Show Login Page
router.get("/login", function (req, res) {
  res.render("login", { user: req.user || null });
});

// POST /users/login -> Handle Login
router.post("/login", passport.authenticate("local", {
  successRedirect: "/users/profile",
  failureRedirect: "/users/login",
  failureFlash: true
}));

// GET /users/profile -> User Profile (Protected)
router.get("/profile", isAuthenticated, function (req, res) {
  res.render("profile", { user: req.user });
});

// GET /users/logout -> Logout
router.get("/logout", function (req, res, next) {
  req.logout(function (err) {
    if (err) {
      return next(err);
    }
    res.redirect("/");
  });
});

// Middleware to Protect Routes
function isAuthenticated(req, res, next) {
  if (req.isAuthenticated()) {
    return next();
  }
  res.redirect("/users/login");
}

module.exports = router;
