<style>
* {
    font-family: "Times New Roman", Times, serif;
}

h1 {
    font-size: 50px !important;
    text-align: center;
}

h2 {
    font-size: 40px !important;
}

h3 {
    font-size: 30px !important;
}

* {
    font-size: 20px !important;
}

p {
    text-indent: 2em;
    line-height: 2;
}

img {
    width: 100%;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

</style>

# Investigation in the thermodynamics of commercial jet engines

## Abstract

Jet engines are widely used in commercial aviation for their high efficiency relative to their size and complexity and reliability. The thermodynamics of these engines is a complex topic that has been investigated by many engineers. As a result, many types of jet engines have been developed over the years, each with its unique characteristics and operating principles. All these theories, however, become only a small part of the complex economics of commercial aviation. This paper will focus on theoretical values and commercial manifestations of jet engines.

## Method

### Theoretical calculations

Thermodynamics, Thired Edition (SI Version), by William Z. Black and James G. Hartley has outlined a great way to calculate the efficiency of an open Brayton cycle, listed on page 424, Example 7.7. The process can be summarized as follows:

![graph for reference](https://media.discordapp.net/attachments/782951565769834569/1105466125057269891/image.png)

> Graph for reference

Using
- Velocity of the aircraft
- Air temperature (at cruising altitude)
- Pressure (at cruising altitude)
- Inlet and exit areas of the engine
- Compressor ratio
- Inlet temperature to the turbine

Calculate
- Mass flow rate of air
- Theoretical thrust
- Power output of the turbine
- Heat flow rate
- Theoretical efficiency

Using the fact that state 1 and 3 are connected by an isentropic path, calculate the ratio of reduced pressure values

```py
# states 1 and 3 are connected by an isentropic path
P13r = P3 / P1

# Temperature at state 3 may be determined using reduced pressure value
Pr1 = temp_to_p_r(T1)
Pr3 = P13r * Pr1
T3 = p_r_to_temp(Pr3)
H3 = temp_to_h(T3)
```

Using the fact that state 4 and 6 are connected by an isentropic path, apply the same method

```py
# states 4 and 6 are connected by an isentropic path
P64r = P6 / P4
Pr4 = temp_to_p_r(T4)
H4 = temp_to_h(T4)
Pr6 = P64r * Pr4
T6 = p_r_to_temp(Pr6)
```

The mass flowrate can be calculated via

```py
# mass flow rate
mass_flowrate = (P1 / (R * T1)) * self.inlet_area * velocity

V6 = mass_flowrate * R * T6 / (P6 * self.exit_area)
```

The theoretical thrust can be calculated via

```py
# unit N
thrust = mass_flowrate * (V6 - velocity)
```

Power output of the turbine can be calculated via

```py
# unit: kW
power = thrust * velocity / 1000
```

Heat flow rate can be calculated via

```py
# unit: kW
heat_flowrate = mass_flowrate * (H4 - H3)
```

Finally, the theoretical efficiency can be calculated via

```py
efficiency = power / heat_flowrate * 100
```

Full code can be found in `src/jet_engine.py`.

Using these variables, it is possible to generate a graph of any two engine variables with some variable of interest being the third axis.

### Data collection

The data has already downloaded and parsed *Aircraft database*, which is a global database of aircraft and engine models (https://github.com/jbroutier/aircraft-database). It has more than 5,200 aircraft models and 4,300 engine models. The parsing algorithm can be found in `src/db.py`. The data is stored in `data/*.json` as JSON files.

### Plotting and analysis

`matplotlib` has beed used to plot the data. After plotting the data, the graph is overlaid on top of a heatimage of some theoretical value given the two parameters used to plot the x and y axis. Heatmaps are constructed using HSV and manipulating the hue while fixing saturation and value to 1. The pixel data is rendered on the final image using PIL (python pillow library). The plotting algorithm can be found in `src/plot.py`.

# Results

Due to my lack of expertise in the field of thermodynamics, I am unable to properly verify nor explain some quirks in the plots. Therefore, I will only be presenting the plots that I find meaningful and valid. All plots can be found in `plots/`.

## Plots and comments

---

## Compresser ratio vs. x with various engine parameters

![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20compresser_ratio-weight%20bg-efficiency.png?raw=true)
![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20compresser_ratio-weight%20bg-heat_flowrate.png?raw=true)
![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20compresser_ratio-weight%20bg-mass_flowrate.png?raw=true)
![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20compresser_ratio-weight%20bg-power.png?raw=true)
![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20compresser_ratio-weight%20bg-thrust.png?raw=true)

Compressor ratio has minimal effect on all dependent variables except heatflow

---
## Inlet area vs. x with various engine parameters

![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20inlet_area-compresser_ratio%20bg-efficiency.png?raw=true)

> A void in the middle can be seen, where inlet area of 4 and compresser ratio of around 363 does not exist

![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20inlet_area-compresser_ratio%20bg-power.png?raw=true)
![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20inlet_area-compresser_ratio%20bg-thrust.png?raw=true)

> In power and thrust plots, many passenger aircrafts are on the green area

---
## Inlet area vs. weight with efficiency

![plot](https://github.com/nopeless/jet-engine-analysis/blob/main/plots/plot%20of%20inlet_area-weight%20bg-efficiency.png?raw=true)

There is a strong correlation between inlet area and weight, with a few outliers being A330 Beluga XL and L-1011 TriStar

For A330 Beluga XL, it seems that the craft operates at a lower speed and simply has greater weight to support larger cargo. More variable analysis is needed for the exact behavior of large cargo aircrafts.

# Limitations

Some calculations do not add to proper values mainly due to the fact that the paper relies on a single model of jet engines to cover a variety of jet engine types. A lot of the engine parameters are fixed despite aircrafts having different operating altutides, speed, and fuel consumption. The real efficiency of the aircraft has not been compared to the theoretical efficiency due to it being absent in the database.

# Conclusion

The data collected from the database has much more processing ahead. Careful analysis of existing aircraft can give insight into the design of future aircrafts and help business models target the right parameters for their aircrafts.

---
This project is avaliable at https://github.com/nopeless/jet-engine-analysis