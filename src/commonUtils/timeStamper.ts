export function getCurrentTimestamp() {
    const time = new Date();
    const dateStamp = `${time.getFullYear()}-${String(time.getMonth() + 1).padStart(2, "0")}-${String(time.getDate()).padStart(2, "0")}`;
    const hmsStamp = `${String(time.getHours()).padStart(2, "0")}:${String(time.getMinutes()).padStart(2, "0")}:${String(time.getSeconds()).padStart(2, "0")}.${String(Math.floor(time.getMilliseconds() / 10)).padStart(2, "0")}`;
    return `${dateStamp} ${hmsStamp}`;
}