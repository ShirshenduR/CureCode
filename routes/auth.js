const express = require("express");
const passport = require("passport");
const User = require("../models/User");
const router = express.Router();

router.post("/register", async (req, res) => {
  try {
    const newUser = new User({ username: req.body.username, password: req.body.password });
    await newUser.save();
    res.redirect("/login");
  } catch (err) {
    res.send("Error registering user");
  }
});

router.post("/login", passport.authenticate("local", {
  successRedirect: "/dashboard",
  failureRedirect: "/login"
}));

router.get("/logout", (req, res) => {
  req.logout(() => res.redirect("/login"));
});

module.exports = router;
