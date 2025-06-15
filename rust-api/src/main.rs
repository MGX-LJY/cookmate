use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Serialize, Deserialize, Clone)]
struct Recipe {
    name: String,
    category: Option<String>,
    method: Option<String>,
    difficulty: Option<String>,
}

struct AppState {
    recipes: Mutex<HashMap<String, Recipe>>,
}

#[get("/ping")]
async fn ping() -> impl Responder {
    HttpResponse::Ok().body("pong")
}

#[get("/recipes")]
async fn list_recipes(data: web::Data<AppState>) -> impl Responder {
    let recipes = data.recipes.lock().unwrap();
    let names: Vec<String> = recipes.keys().cloned().collect();
    HttpResponse::Ok().json(names)
}

#[post("/recipes")]
async fn add_recipe(data: web::Data<AppState>, item: web::Json<Recipe>) -> impl Responder {
    let mut recipes = data.recipes.lock().unwrap();
    recipes.insert(item.name.clone(), item.into_inner());
    HttpResponse::Created().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let app_state = web::Data::new(AppState {
        recipes: Mutex::new(HashMap::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .service(ping)
            .service(list_recipes)
            .service(add_recipe)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
