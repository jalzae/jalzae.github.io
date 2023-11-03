//TODO cara agar sebuah form pesan itu tertulis di pesan


//1 kita harus buat input dan dapatkan elemennya
const name=document.getElementById('name')
const message =document.getElementById('message')
const listPesan=document.getElementById('list_pesan')

//2 buat fungsi untuk meletakkan pesan kedalam list

const forms =document.getElementById('forms')

forms.onsubmit = (e) => {
  
  e.preventDefault()
  if(name.value==''){
    alert('nama kamu kosong')
    return
  }
  
  if(message.value==''){
    alert('pesan kamu kosong')
    return
  }
  
  list_pesan.innerHTML+=`<li> ${name.value} :  ${message.value}</li>`
  
  name.value=''
  message.value=''
}