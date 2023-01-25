//Script for the point adding interface

let buttonID = 0
let item = ''
let gridValue = ''
let savedLocation = ''
let auto = false
let previousCone = 0
let previousCube = 0
let previousAuto = 0
let previousScore = 0

function updateDontMind(){
    $('#lowerCubek').val($('#lowerCube').text())
    $('#middleCubek').val($('#middleCube').text())
    $('#upperCubek').val($('#upperCube').text())
    $('#lowerConek').val($('#lowerCone').text())
    $('#middleConek').val($('#middleCone').text())
    $('#upperConek').val($('#upperCone').text())
    $('#lowerAutok').val($('#lowerAuto').text())
    $('#middleAutok').val($('#middleAuto').text())
    $('#upperAutok').val($('#upperScore').text())
    $('#lowerScorek').val($('#lowerScore').text())
    $('#middleScorek').val($('#middleScore').text())
    $('#upperScorek').val($('#upperScore').text())
}

function stopInput(){
    var x = Number.parseInt($('#inputField').val())
    if (x<0){
        $('#inputField').val(0)
    }
    
}

function updateScore(savedLocation, autonomous, update, verify){
    if (savedLocation.indexOf('l') == 1){
        var scoreLocation = '#lowerScore'
        var location = 'lower'
        var multiplier = 2
    }
    else if (savedLocation.indexOf('m') == 1){
        var scoreLocation = '#middleScore'
        var location = 'middle'
        var multiplier = 3
    }
    else{
        var scoreLocation = '#upperScore'
        var location = 'upper'
        var multiplier = 5
    }
    if (verify){
        if ($('#'+location+'Cone').text() == '0' && $('#'+location+'Cube').text() == '0'){
            $(scoreLocation).text(0)
            $('#' + location + 'Auto').text(0)
            return 0
        }
    }
    if (autonomous){
        multiplier = multiplier + 1
    }
    
    if (update){
        previousCone = Number.parseInt($('#'+location+'Cone').text())
        previousCube = Number.parseInt($('#'+location+'Cube').text())
        previousAuto = Number.parseInt($('#'+location+'Auto').text())
        previousScore = Number.parseInt($(scoreLocation).text())
    }

    else{
        var coneTotal = Number.parseInt($('#'+location+'Cone').text())
        var cubeTotal = Number.parseInt($('#'+location+'Cube').text())
        var newCone = coneTotal - previousCone
        var newCube = cubeTotal - previousCube
        var score =  previousScore + multiplier*(newCone + newCube)
        $(scoreLocation).text(score)
        if (autonomous){
            autoGrid = '#' + location + 'Auto'
            $(autoGrid).text(previousAuto + multiplier*(newCone + newCube))
        }
    }
}

function idel(e){
    buttonID = e.id
    event.preventDefault
}

function tablePlotter(item, gridValue){
    if (item == '#cone'){
        var gridPointValue = '#' + gridValue.substring(1) + 'Cone'
    }
    else if (item == '#cube'){
        var gridPointValue = '#' + gridValue.substring(1,) + 'Cube'
    }
    else{
        $('#warningText').show()
        var gridPointValue = '#' + gridValue.substring(1) + 'Cone'
    }

    return gridPointValue
}

$('input.dontMind').hide()

$().ready(function(){
    $('button.itemButton').click(function(){
        item = '#'+buttonID
        
        $(item).css('background-color','green')

        var idList = ['#cone', '#cube']

        for (let i = 0; i < idList.length; i++){
            if (item != idList[i]){
                $(idList[i]).css('background-color', 'black')
            }
        }

        savedLocation = tablePlotter(item,gridValue)
        $('#inputField').val(Number.parseInt($(savedLocation).text()))
        event.preventDefault()
    })

    $('button.gridButton').click(function(){
        gridValue = '#' + buttonID 

        $(gridValue).css('background-color','#5E232A')

        var idList = ['#lower', '#middle', '#upper']

        for (let i = 0; i < idList.length; i++){
            if (gridValue != idList[i]){
                $(idList[i]).css('background-color', 'black')
            }
        }

        savedLocation = tablePlotter(item,gridValue)
        $('#inputField').val(Number.parseInt($(savedLocation).text()))
        event.preventDefault()
    })

    $('button.plusMinus').click(function(){
        var x = $('#inputField').val()
        updateScore(savedLocation, auto, true,false)
        if (buttonID == 'plus'){
            $('#inputField').val(++x)
        }
        else{
            $('#inputField').val(--x)
        }
        x = $('#inputField').val()
        stopInput()
        x = $('#inputField').val()
        $(savedLocation).text(x)
        updateScore(savedLocation, auto, false,false)
        updateScore(savedLocation,auto,false,true)
        updateDontMind()
        event.preventDefault()
    })

    $('button.autoButton').click(function(){
        if (buttonID == 'autoButton'){
            auto = true
            $('#autoButton').css('background-color', '#1e81b0')
            $('#teleButton').css('background-color', 'black')

        }
        else{
            auto = false
            $('#autoButton').css('background-color', 'black')
            $('#teleButton').css('background-color', '#1e81b0')
        }
        event.preventDefault()
    })
})


//Script for the spreadsheet

const scriptURL = 'https://script.google.com/macros/s/AKfycbzDM7_ofdQMFNwFuNJau6wZFGSRao3poRkkDVyUkf19dUtklNCFsmQIF1IuISOnzl1L_Q/exec'
                const form = document.forms['scoutForm']
              
                form.addEventListener('submit', e => {
                  e.preventDefault()
                  fetch(scriptURL, { method: 'POST', body: new FormData(form)})
                    .then(response => alert('Successfully Submitted!', response) & location.reload())
                    .catch(error => console.error('Error!', error.message))
                })

