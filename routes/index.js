var express = require("express");
var router = express.Router();

// Sample route for homepage
router.get("/", function (req, res) {
  res.render("index", { user: req.user || null, extractedData: null });
});

module.exports = router;
