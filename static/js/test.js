document.write('单引号字符串<br>')
document.write("双引号字符串<br>")
document.write(666)
document.write('<br>')
document.write(666.66)
document.write('<br>')
document.write(true)
document.write('<br>')
document.write(false)
document.write('<br>')

var nname='lsp'
var age=17, ismale=true
var v1$=6, v$1=66, $v1=666

document.write(nname)
document.write('<br>')
document.write(age)
document.write('<br>')
document.write(ismale)
document.write('<br>')
document.write(v1$)
document.write('<br>')
document.write(v$1)
document.write('<br>')
document.write($v1)
document.write('<br>')
document.write('<br>')

function test(v) {
    document.write(3/2)
    document.write('<br>')
    document.write(Math.abs(3/2))
    document.write('<br>')
    document.write(Math.abs(3/(-2)))
    document.write('<br>')
    document.write((3/(-2)))
    document.write('<br>')
    document.write(parseInt('62626.626'))
    document.write('<br>')
    document.write(parseFloat('62626.626'))
    document.write('<br>')
    document.write('<br>')   
    document.write(v)
}

var v=prompt('input')
alert('输入成功')
test(v)
