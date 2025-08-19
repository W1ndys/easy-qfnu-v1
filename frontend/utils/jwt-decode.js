// utils/jwt-decode.js - 兼容微信小程序版本
// 微信小程序兼容的base64解码函数
function base64Decode(str) {
  // 微信小程序提供的base64解码
  if (typeof wx !== 'undefined' && wx.arrayBufferToBase64) {
    try {
      // 使用微信小程序的API
      const buffer = wx.base64ToArrayBuffer(str);
      const uint8Array = new Uint8Array(buffer);
      let result = '';
      for (let i = 0; i < uint8Array.length; i++) {
        result += String.fromCharCode(uint8Array[i]);
      }
      return result;
    } catch (e) {
      // 如果微信API失败，使用fallback
    }
  }

  // Web环境或微信API不可用时的fallback
  if (typeof atob !== 'undefined') {
    return atob(str);
  }

  // 纯JavaScript实现的base64解码（兼容性最好）
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let result = '';
  let i = 0;

  str = str.replace(/[^A-Za-z0-9+/]/g, '');

  while (i < str.length) {
    const encoded1 = chars.indexOf(str.charAt(i++));
    const encoded2 = chars.indexOf(str.charAt(i++));
    const encoded3 = chars.indexOf(str.charAt(i++));
    const encoded4 = chars.indexOf(str.charAt(i++));

    const bitmap = (encoded1 << 18) | (encoded2 << 12) | (encoded3 << 6) | encoded4;

    const byte1 = (bitmap >> 16) & 255;
    const byte2 = (bitmap >> 8) & 255;
    const byte3 = bitmap & 255;

    result += String.fromCharCode(byte1);
    if (encoded3 !== 64) result += String.fromCharCode(byte2);
    if (encoded4 !== 64) result += String.fromCharCode(byte3);
  }

  return result;
}

function b64DecodeUnicode(str) {
  try {
    const decoded = base64Decode(str);
    return decodeURIComponent(
      decoded.replace(/(.)/g, function (m, p) {
        var code = p.charCodeAt(0).toString(16).toUpperCase();
        if (code.length < 2) {
          code = "0" + code;
        }
        return "%" + code;
      })
    );
  } catch (err) {
    // 如果Unicode解码失败，直接返回base64解码结果
    return base64Decode(str);
  }
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
      throw new Error("Illegal base64url string!");
  }

  try {
    return b64DecodeUnicode(output);
  } catch (err) {
    console.warn('Unicode解码失败，尝试直接base64解码:', err);
    return base64Decode(output);
  }
}

export function decode(token) {
  console.log('开始解析JWT token...');

  if (typeof token !== 'string') {
    console.error('Token不是字符串类型:', typeof token);
    throw new Error('Invalid token specified');
  }

  if (!token || token.trim() === '') {
    console.error('Token为空');
    throw new Error('Token is empty');
  }

  const parts = token.split(".");
  console.log('Token分割结果:', parts.length, '个部分');

  if (parts.length !== 3) {
    console.error('JWT格式错误，应该有3个部分，实际有:', parts.length);
    throw new Error("JWT must have 3 parts");
  }

  try {
    const decoded = base64UrlDecode(parts[1]);
    console.log('Base64解码成功');

    if (!decoded) {
      console.error('Base64解码结果为空');
      throw new Error("Cannot decode the token.");
    }

    const payload = JSON.parse(decoded);
    console.log('JWT解析成功，payload:', payload);

    // 检查token是否过期
    if (payload.exp) {
      const now = Math.floor(Date.now() / 1000);
      if (payload.exp < now) {
        console.error('Token已过期，过期时间:', new Date(payload.exp * 1000), '当前时间:', new Date());
        throw new Error('Token has expired');
      }
    }

    return payload;
  } catch (error) {
    console.error('JWT解析失败:', error);
    throw error;
  }
}

// 新增：验证token有效性的辅助函数
export function isTokenValid(token) {
  try {
    decode(token);
    return true;
  } catch (error) {
    console.log('Token验证失败:', error.message);
    return false;
  }
}