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



  
  //************************** UI **************************//
  function remove_chosen_word(w_elt){
    var w = w_elt.text();
    var sort_word_method = sort_word
    if(window.play_mode=='C')
      sort_word_method = sort_phoneme
    var reste = sort_word_method(w+extract_reste());
    //pour chaque mot visible, mettre à jour le reste
    $("ul.liste-anagrammes li:visible").each(function(){
      var this_w = $(this).find("a.add-word");
      if(window.play_mode=='C'){
        this_w = this_w.next('span.api').text();
        this_w = this_w.substr(1,this_w.length-2)
      }else{
        this_w = this_w.text();
      }
      var sw = sort_word_method(this_w);
      var diff = difference(sw, reste);
      $(this).find("span.w-reste").text(diff);
    });
    //pour chaque mot invisible, mettre à jour le reste
    $("ul.liste-anagrammes li.unwritable").each(function(){
      var this_w = $(this).find("a.add-word");
      if(window.play_mode=='C'){
        this_w = this_w.next('span.api').text();
        this_w = this_w.substr(1,this_w.length-2)
      }else{
        this_w = this_w.text();
      }
      var sw = sort_word_method(this_w);
      var diff = difference(sw, reste);
      if (diff===false){
        // console.log("erreur l.134: "+w+" mot:"+this_w+" dans l'ordre: "+sw+" reste:"+reste+" difference:"+diff);
      }else{
        //à l'aide du mot qui vient d'être supprimé,
        //on peut écrire ce mot: le rendre visible
        $(this).find("span.w-reste").text(diff);
        $(this).removeClass("unwritable");
        //$(this).show();
      }
    });
    $(w_elt.parent()).remove();
    $("span.rest-words-count").text($("ul.liste-anagrammes li:visible").length);
    set_reste(reste);
  }
  // w jquery element, clicke event initier (link in first column)
  function chose_word(w){
    var sorted_chosen_word = ""
    var reste = ""
    // alert(window.play_mode);
    //calcul du reste de lettres/phonemes de la page
    if (window.play_mode=="A"){
      // alert(w);
      // alert(w.text());
      sorted_chosen_word = sort_word(w.text());
      reste = difference(sorted_chosen_word, extract_reste());
      if (reste==false){
        console.log("erreur l. 181 "+w.text()+" "+sorted_chosen_word+" "+reste);
      }
    } else{
      api = w.next("span.api").text();
      sorted_chosen_word = sort_phoneme(api.substr(1, api.length-2));
      // console.log("extracted reste: " + sort_phoneme(extract_reste()));
      reste = difference(sorted_chosen_word, sort_phoneme(extract_reste()));
    }
      console.log("chose word: "+sorted_chosen_word)
      console.log('reste: '+reste)
    if(reste==false){
      if(reste===false){
        //todo: w n'est pas dans la liste et
        // une au moins de ses lettres n'est pas dans le reste: on ne peut pas l'écrire
        //en théoie, ça ne se produit que si on ajoute un mot qui n'est pas danns la liste
        alert("impossible d'écrire " + w.text() +  " avec " + extract_reste());
        return false;
      }else{
        //todo: plus aucun mot ne peut etre écrit
        //cacher toutes les lignes du tableau
        //indiquer un joli message de félicitations pour un perfect
        alert("perfect");
        // TODO: ici, ça coince. S'inspirer du "else" ci-dessous:
        //cacher toutes les lignes avec la classe unwritable et
        //mettre à jour tous les restes (null)
        var rows = $("table.table-lemmes tbody tr");
        if(rows.length == 0){
          rows = $("ul.liste-anagrammes li");
        }
        rows.each(function(){
          $(this).addClass("unwritable");
          //$(this).find('td.reste').text(diff);
        });
      }
    }else{
      // on parcourt la liste pour:
      //  -mettre à jour les restes de chaque elt
      //  -cacher les mots qui ne peuvent plus être écrits
      $("ul.liste-anagrammes li").each(function(){
        var reste_row =""
        var word_row="";
        reste_row = $(this).find('span.w-reste').text();
        if(window.play_mode=="A"){
          word_row = $(this).find("a.add-word").text();
        }else{
          word_row = $(this).find("a.add-word").next("span.api").text();
          //replaced substr by susbtring below
          //not sure comportment is the same
          word_row = word_row.substring(1, word_row.length-2);
        }
        if( reste_row ==  "" || !can_write(sort_word(word_row), reste) ){
          //on ne peut plus écrire le mot: le cacher
          $(this).addClass("unwritable");
          //$(this).hide();
        }
        else{
          // ce mot peut encore être écrit
          // on le laisse visible mais il faut mettre son reste à jour
          diff = difference(sorted_chosen_word, reste_row);
          if(diff==false)
            console.log("erreur l.231: *"+word_row+"* *"+ sorted_chosen_word+"* *"+reste_row+"*");
          $(this).find('span.w-reste').text(diff);
        }
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
    var new_wb='';
    //on crée le nouvel élément à ajouter au breadcrumb
    if(window.play_mode=='A')
      new_wb = $('<span class="word-block"><span class="word">'+w.text()+'</span><a href="?remove='+w.text()+'" class="remove_word" title="bye bye \''+w.text()+'\'!">x</a></span>');
    else{
      api = w.next('span.api').text();
      api = api.substr(1,api.length-2)
      new_wb = $('<span class="word-block"><span class="word">'+w.text()+'</span><span class="word-api">'+api+'</span><a href="?remove='+api+'" class="remove_word" title="bye bye \''+w.text()+'\'!">x</a></span>');
    }

    new_wb.hover(function(){
      $(this).find('a.remove_word').show();}
    ,function(){
      $(this).find('a.remove_word').hide();
    });

    new_wb.find("a.remove_word").click(remove_word_click_event);
    
    var last_word = $("div#chosen span.word-block:last");
    if(last_word.length==0)
      last_word = $("div#chosen p");
    last_word.after(new_wb);
    $("span.rest-words-count").text($("ul.liste-anagrammes li:visible").length);
  }
  function remove_word_click_event(event){
    event.preventDefault();
    //peut-être, la ligne du dessous est spécifique au mode anagramme
    //remove_chosen_word($(this).prev('span.word'));
    remove_chosen_word($(this).prev('span'));
    update_natures_count();
  }
  //************************** TRI **************************//
  function alpha_compare(a, b, up = 1, display="table") {
    if(display==table){
      a = $($(a).find('td')[0]).find('a').text().toLowerCase();
      b = $($(b).find('td')[0]).find('a').text().toLowerCase();
    }else{
      a = $($(a).find('a.add-word')).text().toLowerCase();
      b = $($(b).find('a.add-word')).text().toLowerCase();
    }
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
  }
  function length_compare(a, b, up = 1, display="table") {
    if(display==table){
      a = $($(a).find('td')[0]).find('a').text().length;
      b = $($(b).find('td')[0]).find('a').text().length;
    }else{
      a = $($(a).find('a.add-word')).text().length;
      b = $($(b).find('a.add-word')).text().length;
    }
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
  }
  function nature_compare(a, b, up = 1, display="table") {
    a = $($(a).find('td')[1]).text();
    if (a.startsWith('flex-'))
      a = a.substr(5);
    b = $($(b).find('td')[1]).text();
    if (b.startsWith('flex-'))
      b = b.substr(5);
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      
  }
  function genre_compare(a, b, up = 1, display="table") {
    a = $($(a).find('td')[2]).text();
    b = $($(b).find('td')[2]).text();
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      // return up * (($(b).text()) <
      //         ($(a).text()) ? 1 : -1);
  }
  function nombre_compare(a, b, up = 1, display="table") {
    a = $($(a).find('td')[3]).text();
    b = $($(b).find('td')[3]).text();
    if(a == b)
      return 0;
    return up * (( b < a) ? 1 : -1);
      // return up * (($(b).text()) <
      //         ($(a).text()) ? 1 : -1);
  }
  sort_functions_index = {"alpha": alpha_compare, "length": length_compare};
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

  //sort_rows and sort_litems are twins
  //the only difference is that sort_litems
  //set the "display" parameter to "list"
  //in order to get the correct jQuery selector
  function sort_rows(a, b){
    // console.log("sorting");
    // console.log(a);
    // console.log(b);
    for(i=0;i<sort_functions.length;i++){
      // console.log(sort_functions[i]["func"]);
      var r = sort_functions_index[sort_functions[i]["func"]](a,b,sort_functions[i]['up']);
      if (r!=0)
        return r;
    }
    return 0;
  }
  function sort_litems(a,b){
    for(i=0;i<sort_functions.length;i++){
      // console.log(sort_functions[i]["func"]);
      var r = sort_functions_index[sort_functions[i]["func"]](a,b,sort_functions[i]['up'], 'list');
      if (r!=0)
        return r;
    }
    return 0;
  }
  /************************** Filtres **************************/

  /* show, hide: list of "natures" values to be shown or hidden */
  function filter_by_nature(show, hide){
    $("table.table-lemmes tbody tr.filtered").each(function(){
      if(show.indexOf($(this).find("td.nature").text()) != -1)
        $(this).removeClass("filtered");
    });
    $("table.table-lemmes tbody tr").not(".filtered").each(function(){
      if(hide.indexOf($(this).find("td.nature").text()) != -1)
        $(this).addClass("filtered");
    });
    var fltd_elts_cnt = $("table.table-lemmes tbody tr.filtered:not(.unwritable)").length;
    console.log(fltd_elts_cnt + " elements filtered");
  }

  //**************************  **************************//
  $(document).ready(function(){
    window.play_mode = "A" //anagrammes_liste
    mmode = $('label[for=phrase]').text();
    if(mmode.search('contrepeter')!=-1){
      window.play_mode = "C";
    }
     $("a.add-word").click(function(event){
       event.preventDefault();
       word = event.target.innerText;
       chose_word($(event.target));
     });
     $("a.remove_word").click(remove_word_click_event);
    
    //make chosen words manually sortable
    //so that user is able to chose their order
    $("#chosen").sortable();
    $('span.word-block').hover(function(){
      $(this).find('a.remove_word').show();}
    ,function(){
      $(this).find('a.remove_word').hide();
    });
    //TODO: done permettre de réorganiser l'ordre d'application des fonctions de tri
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
      if (sort_functions.length > 0){
        var xx = $("ul.liste-anagrammes li").sort(sort_litems);
        xx.appendTo('ul.liste-anagrammes');
      }

    });
    

  })
