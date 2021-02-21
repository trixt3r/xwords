$(document).ready(function(){
  $("ul#faq li a.question").click(function(event){
    event.preventDefault();
    console.log("id question: " + event.target.id);
    $("div#devant-tout").append($("p#answer-"+event.target.id));
    console.log($("p#answer-"+event.target.id))
    $("div#devant-tout").show();
  });
  $("a.exit-faq").click(function(event){
    event.preventDefault();
    $(event.target).parent("p").next("p").appendTo("div#faq-answers");
    $("div#devant-tout").hide();
  });
});
