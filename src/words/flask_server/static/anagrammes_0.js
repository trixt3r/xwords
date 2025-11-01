//this function create a http query arg which contains the
//list of words already chosen by user
  function create_chosen_words_arg(){
    words = $("span.word");
    arg = "";
    for(i=0;i<words.length;i++){
      if(i>0)
        arg += ",";
      arg += words[i].innerText;
    }
    return arg;
  }
  //extract url parameter by name
  function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
      sURLVariables = sPageURL.split('&'),
      sParameterName,
      i;

    for (i = 0; i < sURLVariables.length; i++) {
      sParameterName = sURLVariables[i].split('=');

      if (sParameterName[0] === sParam) {
        return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
      }
    }
    return undefined;
  };
  var sort_functions = [];



  //************************** Specifique Anagramme **************************//
  //return true if b can write a
  //else false
  function can_write(a, b){
    return difference(a, b, true);
  }
  //return b - a
  //return false if b cannot write a
  function difference(a, b, can_write_flag=false){
    var j=0, i=0, result = "";
    for(;i<a.length;i++){
      c = a[i];
      while(!(b[j] == c)){
        result += b[j];
        j++;
        if(j>=b.length)
          break;
      }
      j++;
      if(j>b.length)
        break;
    }
    if(i!=a.length){
      //todo: le cas a == b passe par ici
      //il ne devrait pas
      console.log(i+" "+a.length)
      console.log(j+" "+b.length)
      return false;}
    if(can_write_flag)
      return true;
    for(;j<b.length;j++)
      result += b[j];
    return result;
  }
  function remove_accents_word(w){
    result = ""
    accents = {"e": "éèêë",
          "a": "âà",
          "i": "îï",
          "o": "öô",
          "u": "ûù",
          "c": "ç"}
    var found = false;
    var keys = Object.keys(accents);
    for(i=0;i<w.length;i++){
      for(k=0;k<keys.length;k++){
        if(accents[keys[k]].includes(w[i])){
          result += keys[k];
          w[i] = keys[k];
          found = true;
          break;
        }
      }
      if(found){
        found = false;
        continue;
      }
      result += w[i];
    }
    return result;
  }
  function sort_word(w, accents=false){
    letters = []
    if(accents == false){
      w = remove_accents_word(w);
    }
    for(i=0;i<w.length;i++){
      letters.push(w[i]);
    }
    console.log(letters);
    letters.sort();
    return letters.join("");
  }

  function sort_phoneme(){

  }
  //************************** UI **************************//
  function remove_chosen_word(w_elt){
    w = w_elt.text();
    alert(w);
    var reste = sort_word(w+extract_reste())
    $("table.table-anagrammes tbody tr:hidden").each(function(){
      sw=sort_word($(this).find("a.add-word"));
      if(can_write(sw, reste)){
        $(this).find("td.reste").text(difference(reste, sw));
        $(this).show();
      }
    });
    w_elt.parent.remove();
    set_reste(reste);
  }
  function chose_word(w){
    var sorted_word = sort_word(w);
    var reste = difference(sorted_word, extract_reste())
    if(reste==false){
      if(reste===false){
        //todo: w n'est pas dans la liste et
        // une au moins de ses lettres n'est pas dans le reste: on ne peut pas l'écrire
        alert("impossible d'écrire " + w +  " avec " + extract_reste());
        return false;
      }else{
        //todo: plus aucun mot ne peut etre écrit
        //cacher toutes les lignes du tableau
        //indiquer un joli message de félicitations pour un perfect
        alert("perfect");
        $("table.table-anagrammes tbody tr").each(function(){$(this).hide();});
      }
    }else{
      $("table.table-anagrammes tbody tr").each(function(){
        reste_row = $(this).find('td.reste').text();
        word_row = $(this).find("a.add-word").text();
        if( reste_row ==  "" || !can_write(sort_word(word_row), reste) )
          $(this).hide();
        else
          $(this).find('td.reste').text(difference(sorted_word, reste_row));
      });
    }
    set_reste(reste);
    ui_add_chosen_word(w);
  }
  function extract_reste(){
        return $('span#reste').text();
  }
  function set_reste(r){
    $('span#reste').text(r);
  }
  function ui_add_chosen_word(w){
    new_wb = $('<span class="word-block"><span class="word">'+w+'</span><a href="?remove='+w+'" class="remove_word" title="bye bye \''+w+'\'!">x</a></span>');
    new_wb.hover(function(){
      $(this).find('a.remove_word').show();}
    ,function(){
      $(this).find('a.remove_word').hide();
    });
    new_wb.find("a.remove_word").click(remove_word_click_event);
    //todo: ajouter le manager de click sur a.remove_word
    var last_word = $("div#chosen span.word-block:last");
    if(last_word.length==0)
      last_word = $("div#chosen p");
    last_word.after(new_wb);
  }
  function remove_word_click_event(event){
    event.preventDefault();
    remove_chosen_word($(this).prev('span.word'));
  }
  //************************** TRI **************************//
  function alpha_compare(a, b, up = 1) {
    a = $($(a).find('td')[0]).find('a').text().toLowerCase();
    b = $($(b).find('td')[0]).find('a').text().toLowerCase();
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      return up * (($(b).find('a').text().toLowerCase()) <
              ($(a).find('a').text().toLowerCase()) ? 1 : -1);
  }
  function length_compare(a, b, up = 1) {
    a = $($(a).find('td')[0]).find('a').text().length;
    b = $($(b).find('td')[0]).find('a').text().length;
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      return up * (($(b).find('a').text().length) <
              ($(a).find('a').text().length) ? 1 : -1);
  }
  function nature_compare(a, b, up = 1) {
    a = $($(a).find('td')[1]).text();
    if (a.startsWith('flex-'))
      a = a.substr(5);
    b = $($(b).find('td')[1]).text();
    if (b.startsWith('flex-'))
      b = b.substr(5);
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      return up * (($(b).text()) <
              ($(a).text()) ? 1 : -1);
  }
  function genre_compare(a, b, up = 1) {
    a = $($(a).find('td')[2]).text();
    b = $($(b).find('td')[2]).text();
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      return up * (($(b).text()) <
              ($(a).text()) ? 1 : -1);
  }
  function nombre_compare(a, b, up = 1) {
    a = $($(a).find('td')[3]).text();
    b = $($(b).find('td')[3]).text();
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      return up * (($(b).text()) <
              ($(a).text()) ? 1 : -1);
  }
  sort_functions_index = {"alpha": alpha_compare, "length": length_compare, "nature": nature_compare, "genre": genre_compare, "nombre": nombre_compare};
  window.sort_functions = [];
  function set_sort_table_order() {
    sort_functions = [];
    sort_options=["up", "down", "no"];
    var up = 0;
    $("p.sort-options span.sort-option img").each(function(){
      // console.log($(this).attr("class").substr(5));
      sort = $(this).attr('src').split('/').slice(-1)[0].split("_")[1].split('.')[0]
      sort_idx = sort_options.indexOf(sort);
      if(sort_idx == 2)
        // continue
        return true;
      else if (sort_idx == 1)
        up = -1;
      else
        up = 1;
      // console.log("pushing: ");
      // console.log({"func": $(this).attr("class").substr(5),"up": up});
      sort_functions.push({"func": $(this).attr("class").substr(5),"up": up});
    });
    // console.log('fonctions tri choisies:')
    // for(i=0;i<sort_functions.length;i++)
    //   console.log(sort_functions[i]);
  }
  function sort_table_rows(a, b){
    for(i=0;i<sort_functions.length;i++){
      var r = sort_functions_index[sort_functions[i]["func"]](a,b,sort_functions[i]['up']);
      if (r!=0)
        return r;
    }
    return 0;
  }

  //**************************  **************************//
  $(document).ready(function(){
     $("a.add-word").click(function(event){
       event.preventDefault();
       word = event.target.innerText;
       chose_word(word);
     });
     $("a.remove_word").click(remove_word_click_event);
    // $("div#breadcrumb").append("<span>"+create_chosen_words_arg()+"</span>");
    // handler to remove a word
    // $("a.remove_word").click(function(event){
    //     event.preventDefault();
    //     removed = $(event.target).prev("span.word").get(0).innerText;
    //     //add letters of the removed word to the ref_str
    //     //server will sort em
    //     reste = getUrlParameter("reste") + removed;
    //     phrase = getUrlParameter("phrase");
    //     display = getUrlParameter("display");
    //     //remove the word, so that create_chosen_words_arg returns good result
    //     $(event.target).parent("span.word-block").remove();
    //     words = create_chosen_words_arg();
    //     window.location.replace("/anagrammes/?words="+words+"&phrase="+phrase+"&reste="+reste);
    // });
    // handler to chose a word from the list
    // $("a.add-word").click(function(event){
    //   event.preventDefault();
    //   // word newly chosen
    //   word = event.target.innerText
    //   reste = getUrlParameter("reste");
    //   phrase = getUrlParameter("phrase");
    //   words = create_chosen_words_arg();
    //   // the "add" param contains the new word
    //   // so that server is able to remove its letters from the rest
    //   if(reste === undefined) //this is the first word chosen by user
    //     window.location.replace("/anagrammes/?words="+words+"&add="+word+"&phrase="+phrase);
    //   else
    //     window.location.replace("/anagrammes/?words="+words+"&add="+word+"&phrase="+phrase+"&reste="+reste);
    // });
    //make chosen words manually sortable
    //so that user is able to chose their order
    $("#chosen").sortable();
    $('span.word-block').hover(function(){
      $(this).find('a.remove_word').show();}
    ,function(){
      $(this).find('a.remove_word').hide();
    });
    //TODO: permettre de réorganiser l'ordre d'application des fonctions de tri
    $("p.sort-options").sortable();


    //gestion du tri des listes de mots
    $('img.sort').click(function(event){
      sort_options=["up", "down", "no"]
      sort = event.target.getAttribute('src').split('/').slice(-1)[0].split("_")[1].split('.')[0]
      sort_idx = sort_options.indexOf(sort)
      sort_idx = (sort_idx + 1) % 3
      event.target.setAttribute('src', "/static/images/sort_"+sort_options[sort_idx]+".png");
      var up = 1;
      if(sort_idx == 1)
        up = -1;
      set_sort_table_order();
      if (sort_functions.length > 0)
        $("table.table-anagrammes tbody tr").sort(sort_table_rows).appendTo('table.table-anagrammes tbody');

    });
    // $("form[name=custom-word]").submit(function(event){
    //   event.preventDefault();
    //   // word newly chosen
    //   word = $(event.target).find('input[name=add]').get(0).value;
    //   reste = getUrlParameter("reste");
    //   phrase = getUrlParameter("phrase");
    //   words = create_chosen_words_arg();
    //   // the "add" param contains the new word
    //   // so that server is able to remove its letters from the rest
    //   if(reste === undefined){ //this is the first word chosen by user
    //     window.location.replace("/anagrammes/?words="+words+"&add="+word+"&phrase="+phrase);
    //   }else
    //     window.location.replace("/anagrammes/?words="+words+"&add="+word+"&phrase="+phrase+"&reste="+reste);
    // });

  })
