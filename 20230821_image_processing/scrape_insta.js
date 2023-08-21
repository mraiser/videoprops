// Go to a person's instagram page, 
// click on the first post, and 
// paste this into the console

var seen = {};

String.prototype.hashCode = function() {
  var hash = 0,
    i, chr;
  if (this.length === 0) return hash;
  for (i = 0; i < this.length; i++) {
    chr = this.charCodeAt(i);
    hash = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
}

function fetchFile(url, name, cb) {
    fetch(url).then(res => res.blob()).then(file => {
        let tempUrl = URL.createObjectURL(file);
        const aTag = document.createElement("a");
        aTag.href = tempUrl;
        aTag.download = name; //url.replace(/^.*[\\\/]/, '');
        document.body.appendChild(aTag);
        aTag.click();
        URL.revokeObjectURL(tempUrl);
        aTag.remove();
        setTimeout(cb,0);
    }).catch(() => {
        alert("Failed to download file!");
    });
}

function saveJSON(content, fileName) {
    var a = document.createElement("a");
    var file = new Blob([content], {type: 'text/plain'});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}

function mrClickNext(){
  var a = document.getElementsByTagName("svg");
  for (let i=0;i<a.length;i++) { 
    if (a[i].getAttribute('aria-label') == "Next") {
      a[i].parentElement.click();
      return true;
    }
  }
  return false;
}

function mrGetImg(url, desc){
  var name = "a"+desc.hashCode()+"_b"+url.hashCode();
  fetchFile(url, name, function(){
//    saveJSON(desc, name+'.txt');
  });
}

function mrFindImgs(){
  var a = document.getElementsByTagName("img");
  for (let i=0;i<a.length;i++) { 
    if(a[i].width > 309) { 
      var url = a[i].src;
      if (!seen[url]){
        seen[url] = true;
        var desc = ""+a[i].getAttribute('alt');
        mrGetImg(url, desc);
      }
    }
  }
}

//var stopcount = 0;
function mrScrape(){
  mrFindImgs();
//  if (stopcount < 3) 
  if (mrClickNext()) {
//  stopcount++;
    setTimeout(mrScrape, 1000);
  }
}

mrScrape();
