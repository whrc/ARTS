main = st_read("C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.2.0.0/ARTS_main_dataset_firstrowNA.geojson")
main = slice(main, 2:n())

st_write(main, "C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.2.0.0/ARTS_main_dataset.geojson", append=FALSE)