var express = require("express");
var router = express.Router();
var jwt = require("jsonwebtoken");

// Sample route for homepage
router.get("/", function (req, res) {
  res.render("index", { user: req.user || null, extractedData: null });
});

router.get("/dashboard", (req, res) => {
  const token = req.cookies.token;
  if (!token) {
    return res.redirect("/users/login");
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.redirect("/users/login");
    }
    req.user = decoded;
    res.render("dashboard", { user: req.user });
  });
});

module.exports = router;
