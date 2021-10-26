// this to fix modulus bug
function mod(n, m) {
    return ((n % m) + m) % m;
}

function modInverse(a, b) {
    for(let x = 1; x < b; x++)
        if (mod((mod(a,b) * mod(x,b)), b) == 1)
            return x;
}

function Affine(string, a, b) {
    var newStr = ""
    for (let i = 0; i < string.length; i++) {
        newStr += String.fromCharCode(mod((a*(string.charCodeAt(i) - 97) + b), 26) + 97)
    }
    return newStr;
}

function reverseAffine(string, a, b) {
    let newStr = ""
    for (let i = 0; i < string.length; i++) {
        newStr += String.fromCharCode(mod(modInverse(a,26)*(string.charCodeAt(i) -97 - b), 26) + 97);
    }
    return newStr;
}

console.log("start")
console.log(reverseAffine(Affine("money",1123,45),1123,45));
console.log("finish")


