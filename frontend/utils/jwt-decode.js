// utils/jwt-decode.js
function b64DecodeUnicode(str) {
    return decodeURIComponent(
        atob(str).replace(/(.)/g, function (m, p) {
            var code = p.charCodeAt(0).toString(16).toUpperCase();
            if (code.length < 2) {
                code = "0" + code;
            }
            return "%" + code;
        })
    );
}

function base64UrlDecode(str) {
    var output = str.replace(/-/g, "+").replace(/_/g, "/");
    switch (output.length % 4) {
        case 0:
            break;
        case 2:
            output += "==";
            break;
        case 3:
            output += "=";
            break;
        default:
            throw "Illegal base64url string!";
    }

    try {
        return b64DecodeUnicode(output);
    } catch (err) {
        return atob(output);
    }
}

export function decode(token) {
    var parts = token.split(".");
    if (parts.length !== 3) {
        throw new Error("JWT must have 3 parts");
    }
    var decoded = base64UrlDecode(parts[1]);
    if (!decoded) {
        throw new Error("Cannot decode the token.");
    }
    return JSON.parse(decoded);
}