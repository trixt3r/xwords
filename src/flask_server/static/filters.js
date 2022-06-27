
function update_natures_count(){
  $("td.nat-cnt").each(function(){
    var nat = $(this).parents("tr").eq(0).find("td:eq(0)").text();
    console.log("nat: " + nat);
    var rows = $("table.table-lemmes tr." + nat);
    var cnt_all = rows.length;
    var cnt_writable = rows.not(".unwritable").length;
    $(this).text(cnt_writable + "/" + cnt_all);
  });
}

$(document).ready(function(){
  $("div.filters input:checkbox").change(function(){
    var name = $(this).attr('name').split("-");
    var option = name.pop();
    var state = $(this).prop('checked');
    var nat = name.join('-');
    other = nat + (option=='shown'?"-hidden":"-shown");
    $(this).parents('tr').find("input[name="+other+"]").prop('checked', !state);
    console.log("option: "+option+" nature: "+nat);
    if(option=="hidden")
      $("table.table-lemmes td.nature").filter("." + nat).each(function(){
        $(this).parents("tr").eq(0).addClass("filtered");
      });
    if(option=="shown")
      $("table.table-lemmes td.nature").filter("." + nat).each(function(){
        $(this).parents("tr").eq(0).removeClass("filtered");
      });
  });
  update_natures_count();
});
