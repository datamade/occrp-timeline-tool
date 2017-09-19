$(document).ready(function() {
    // Facets panel
    $('.panel-show').addClass('in');
    $('.panel-heading').on('click', function () {
        if ($(this).parent().children().eq(1).hasClass('in')){
            $(this).find('i').removeClass('fa-minus').addClass('fa-plus');
        } else{
            $(this).find('i').removeClass('fa-plus').addClass('fa-minus');
        }
    });

    // Events table
    $('body').on('mouseover', 'tr.detailsControl', function(e){
        $(this).css('background-color', '#f9f9f9')
    });

    $('body').on('mouseout', 'tr.detailsControl', function(e){
        $(this).css('background-color', '#fff')
    });

    $('body').on('click', 'tr.detailsControl', function(e){
        e.stopPropagation();
        target = $(e.target);
        target.closest('tr').next('tr').children().slideToggle(100);

        var right = $(this).find('.fa-chevron-circle-right');
        var down = $(this).find('.fa-chevron-circle-down');

        if(($(right).is(":visible"))) {
            $(this).find('.fa-chevron-circle-down').show();
            $(this).find('.fa-chevron-circle-right').hide();
            $(this).css("font-weight", "700");
        } else {
            $(this).find('.fa-chevron-circle-down').hide();
            $(this).find('.fa-chevron-circle-right').show();
            $(this).css("font-weight", "400");
        }
    });

    // Event form
    // Click on input boxes without triggering collapse
    $('#collapsePeopleOrg').on('click', function(e){
        e.stopPropagation();
    });

    $('#collapseTimePlace').on('click', function(e){
        e.stopPropagation();
    });

    // Add multiple people, organizations, and sources
    function addInput(entityTypeID) {
        input = $(entityTypeID).children().first().clone();
        input.find('input:text').val('');
        $(entityTypeID).append(input);
        $(input).prepend("<div class='col-sm-12 removeRow'><a href=''><i class='fa fa-times' aria-hidden='true'></i> Remove</a></div>");

    } 

    $('#addOrganization').on('click', function(e){
        e.preventDefault();
        addInput('#organizationRow');
    });

    $('#addPerson').on('click', function(e){
        e.preventDefault();
       addInput('#personRow');
    });

    $('#addSource').on('click', function(e){
        e.preventDefault();
        addInput('#sourceRow');
    });

    // Event delegation for dynamically generated items
    $('.panel-body').on('click', '.removeRow', function(e){
        e.preventDefault();
        $(this).parent().remove()
    });

});