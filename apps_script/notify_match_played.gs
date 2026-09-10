function processMatch(e) {
  MailApp.sendEmail({
    to: "example@example.com",
    subject: "Match Played",
    htmlBody: "Another match was played!"
  });
}
