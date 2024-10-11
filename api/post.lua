wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"

-- Функция для генерации случайной строки
function random_string(length)
   local chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
   local result = ''
   for i = 1, length do
      local rand = math.random(#chars)
      result = result .. chars:sub(rand, rand)
   end
   return result
end

request = function()
   local randomQuestion = random_string(10)  -- Генерация случайной строки длиной 10 символов
   local body = '{"question": "' .. randomQuestion .. '"}'
   return wrk.format(nil, nil, nil, body)
end