const express = require("express");
const passport = require("passport");
const User = require("../models/User");

const router = express.Router();

// Register User
router.post("/register", async (req, res) => {
    try {
        const { name, email, password } = req.body;
        const user = new User({ name, email, password });
        await user.save();
        res.redirect("/login");
    } catch (error) {
        res.status(500).send("Error registering user");
    }
});

// Login User
router.post("/login", passport.authenticate("local", {
    successRedirect: "/dashboard",
    failureRedirect: "/login",
    failureFlash: true
}));

// Logout User
router.get("/logout", (req, res) => {
    req.logout(() => {
        res.redirect("/login");
    });
});

module.exports = router;
