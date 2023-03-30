
teamList.sort()

let noOfPages = Math.floor(teamList.length/5) 
let buttonId = 0

if (teamList.length/5 > Math.floor(teamList.length/5)){
  noOfPages += 1 
}

function adjustTheJsonDisplay(page){
  page = page - 1
  let adjustedStarter = 0 + 5*page 
  let adjustedEnder = adjustedStarter + 4
  
  if (adjustedEnder > teamList.length){
    adjustedEnder = teamList.length
  }
  for (let i = 0; i < teamList.length; i++){
    $('#' + teamList[i]).hide()
  }

  for (let i = adjustedStarter; i < adjustedEnder + 1; i++){
    $('#' + teamList[i]).show()
  } 
}

function idel(e){
  buttonId = e.id
  e.preventDefault
}

$().ready(function(){
  var page = 1
  $('#pageIndicator').text(`${page} out of ${noOfPages}`)

  adjustTheJsonDisplay(page)

  $('button').click(function(){
    if (buttonId == 'backPage' && page != 1){
      page -= 1
      adjustTheJsonDisplay(page)
     $('#pageIndicator').text(`${page} out of ${noOfPages}`)
    }
    else if (buttonId == 'movePage' && page + 1 <= noOfPages){
      page += 1
      adjustTheJsonDisplay(page)
      $('#pageIndicator').text(`${page} out of ${noOfPages}`)
    }
  })
})