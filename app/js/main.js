

function fetch_popular() {
  $.ajax({
   type: "GET",
   contentType: "application/json; charset=utf-8",
   url: "/popular",
   async: true,
   success: function (data) {
     console.log(data);
   },
   error: function (err) {

   }
 });
 }
 fetch_popular();
