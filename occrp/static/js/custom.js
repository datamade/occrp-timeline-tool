$(document).ready(function() {
    // $('.collapse').collapse()

    // Todo: not working?
    $("body").on("mouseover", "tr.detailsControl", function(e){
        $(this).css("background-color", "red")
    });

    $("body").on("mouseout", "tr.detailsControl", function(e){
        $(this).css("background-color", "#eee")
    });

    $("body").on("click", "tr.detailsControl", function(e){
        e.stopPropagation();

        var target = $(e.target);

        target.closest('tr').next('tr').children().slideToggle(100);

        // var right = $(this).find('.fa-chevron-circle-right');
        // var down = $(this).find('.fa-chevron-circle-down');

        // if(($(right).is(":visible"))) {
        //     $(this).find('.fa-chevron-circle-down').show();
        //     $(this).find('.fa-chevron-circle-right').hide();
        //     $(this).css("font-weight", "700")
        // } else {
        //     $(this).find('.fa-chevron-circle-down').hide();
        //     $(this).find('.fa-chevron-circle-right').show();
        //     $(this).css("font-weight", "400")
        // }
    });

});