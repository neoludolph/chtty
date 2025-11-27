FROM node:22
WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm install
COPY . . 
EXPOSE 5174
CMD [ "npm", "run", "dev", "--", "--host", "0.0.0.0" ]