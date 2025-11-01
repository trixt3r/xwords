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
        // console.log("cmp "+c+", "+b[j])
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
      //console.log(i+" "+a.length)
      //console.log(j+" "+b.length)
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
  //canonic form
  function sort_word(w, accents=false){
    var letters = []
    w = w.replaceAll('-','');
    if(accents == false){
      w = remove_accents_word(w);
    }
    for(i=0;i<w.length;i++){
      letters.push(w[i]);
    }
    //console.log(letters);
    letters.sort();
    return letters.join("");
  }

  function sort_phoneme(api){
    var letters = [], i = 0;
    while( i<api.length ){
      if(api.charAt(i)=='.')
        i++;
      if (i<api.length-1 && api.charCodeAt(i+1) == 771){
        letters.push(api.substr(i, 2));
        i += 2;
      }else{
        letters.push(api.charAt(i));
        i++;
      }
    }
    letters.sort();
    return letters.join('');
  }