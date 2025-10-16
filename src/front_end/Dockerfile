FROM node:20-alpine

WORKDIR /app
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

COPY package.json package-lock.json ./

RUN npm install --legacy-peer-deps

COPY . .

RUN chmod +x node_modules/.bin/react-scripts

EXPOSE 3000

CMD ["npm", "start"]