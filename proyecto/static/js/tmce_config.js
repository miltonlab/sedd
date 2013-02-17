tinyMCE.init({
    theme : "advanced",
    /*mode : "textareas",*/
    mode : "exact",
    /*encabezado de cuestionario, descripcion de pregunta, texto de pregunta*/
    elements: 'id_encabezado, id_descripcion, id_texto',
    width: "85%",
    height:  "300",
    theme_advanced_buttons3 : "",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons1 : "fullscreen,preview,bold,italic,underline,forecolor,backcolor,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,justifyleft, justifycenter, justifyrigth, justifyfull, separator,undo,redo,separator,link,unlink,anchor,separator,image,media,cleanup,separator,code,table,split_cells,merge_cells",
    //tablecontrols
    plugins: "table, preview, fullscreen",
});